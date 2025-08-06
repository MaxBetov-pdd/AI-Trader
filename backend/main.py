# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Локальные импорты
import logic
from database import async_engine, metadata, users, analyses
from auth import (
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
    UserInDB,
    Token,
    get_db_session,
)

# --- Модели данных Pydantic ---
class AnalysisResultModel(BaseModel):
    id: int
    user_id: int
    symbol: str
    analysis_summary: str
    direction: str
    entry_type: str
    entry_price: str
    stop_loss: float
    take_profit: float
    risk_reward_ratio: str
    invalidation_hours: int
    consensus: str
    status: str

class AnalysisRequest(BaseModel):
    pair: str
    strategy_key: str

# --- СОЗДАНИЕ ПРИЛОЖЕНИЯ (ПЕРЕД ИСПОЛЬЗОВАНИЕМ) ---
app = FastAPI(
    title="AI-Trader API",
    description="API для анализа торговых пар с помощью AI.",
    version="14.1" # Исправленная версия
)

# --- Глобальные переменные и CORS ---
active_analyses_lock = asyncio.Lock()
active_analyses_count = 0
origins = ["*"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# --- События жизненного цикла ---
@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

# --- Эндпоинты ---
@app.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db_session)
):
    query = select(users).where(users.c.username == form_data.username)
    result = await db.execute(query)
    user_in_db_tuple = result.fetchone()

    if not user_in_db_tuple:
        hashed_password = get_password_hash(form_data.password)
        insert_query = users.insert().values(username=form_data.username, hashed_password=hashed_password)
        await db.execute(insert_query)
        await db.commit()
        result = await db.execute(query)
        user_in_db_tuple = result.fetchone()
    
    user_in_db = user_in_db_tuple._asdict()
    if not verify_password(form_data.password, user_in_db['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_in_db['username']})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/analyses/active")
async def get_active_analyses():
    return {"active_count": active_analyses_count}

@app.post("/analyze/")
async def analyze_pair(
    request: AnalysisRequest,
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    global active_analyses_count, active_analyses_lock
    
    async with active_analyses_lock:
        active_analyses_count += 1
    
    try:
        result = await run_in_threadpool(logic.run_full_analysis, request.pair, request.strategy_key)
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        if result.get("status") == "success":
            is_premium_signal = result.get("consensus") == "3/3" and result.get("entry_type") == "Limit"
            insert_query = analyses.insert().values(
                user_id=current_user.id,
                symbol=result["symbol"],
                analysis_summary=result["analysis_summary"],
                direction=result["direction"],
                entry_type=result["entry_type"],
                entry_price=str(result.get("entry_price")) if result.get("entry_price") else "Market",
                stop_loss=result["stop_loss"],
                take_profit=result["take_profit"],
                risk_reward_ratio=result["risk_reward_ratio"],
                invalidation_hours=result["invalidation_hours"],
                consensus=result.get("consensus", "N/A"),
                is_high_quality=is_premium_signal,
            )
            await db.execute(insert_query)
            await db.commit()
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {e}")
    finally:
        async with active_analyses_lock:
            active_analyses_count -= 1

@app.get("/history", response_model=List[AnalysisResultModel])
async def get_user_history(
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    query = select(analyses).where(analyses.c.user_id == current_user.id).order_by(analyses.c.timestamp.desc())
    result = await db.execute(query)
    history_records = result.fetchall()
    return [record._asdict() for record in history_records]
