# -*- coding: utf-8 -*-
# Полное содержимое файла backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logic # Импортируем наш файл с логикой

# --- Создание экземпляра FastAPI ---
app = FastAPI(
    title="AI-Trader API",
    description="API для анализа торговых пар с помощью AI.",
    version="10.0"
)

# --- Настройка CORS ---
# Это важнейший блок, который позволяет вашему сайту (Frontend)
# общаться с этим сервером (Backend).
# Убедитесь, что порт совпадает с тем, на котором работает ваш Frontend (Vite обычно использует 5173).
origins = [
    "http://localhost:3000",  # Для create-react-app
    "http://localhost:5173",  # Для Vite (наш случай)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],
)


# --- Модели данных (Pydantic) ---
# Определяем, какие данные мы ожидаем получить в запросе.
# FastAPI автоматически проверит, что запрос от Frontend соответствует этой структуре.
class AnalysisRequest(BaseModel):
    pair: str
    strategy_key: str


# --- API Эндпоинты ---

@app.get("/")
def read_root():
    """
    Корневой эндпоинт для проверки, что сервер запущен.
    """
    return {"message": "AI-Trader API v10.0. Отправьте POST запрос на /analyze/ для начала работы."}


@app.post("/analyze/")
async def analyze_pair(request: AnalysisRequest):
    """
    Главная точка входа для анализа. 
    Принимает торговую пару и ключ стратегии, возвращает торговый план.
    """
    print(f"Получен запрос: Пара={request.pair}, Стратегия={request.strategy_key}")
    
    # Вызываем нашу основную функцию из файла logic.py
    result = logic.run_full_analysis(request.pair, request.strategy_key)
    
    # 1. Проверяем на ОЖИДАЕМУЮ ошибку (например, неверный ключ стратегии).
    #    Наша функция в logic.py вернет словарь с ключом "error".
    if result.get("error"):
        # Если ключ "error" есть, это ошибка на стороне клиента (Bad Request).
        # Выбрасываем HTTPException с кодом 400. FastAPI перехватит это
        # и вернет клиенту корректный ответ с кодом 400.
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 2. Если в logic.py произойдет НЕОЖИДАННАЯ ошибка (например, API Gemini недоступен),
    #    FastAPI по умолчанию сам перехватит ее и вернет правильный ответ 500 Internal Server Error.
    #    Нам не нужно оборачивать вызов в try-except.
    
    print(f"Отправка результата: {result.get('status')}")
    return result
