# backend/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKey, func, Boolean # <-- Импортируем Boolean

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "mysecretpassword")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, index=True),
    Column("hashed_password", String),
)

analyses = Table(
    "analyses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("symbol", String),
    Column("analysis_summary", String),
    Column("direction", String),
    Column("entry_type", String),
    Column("entry_price", String),
    Column("stop_loss", Float),
    Column("take_profit", Float),
    Column("risk_reward_ratio", String),
    Column("invalidation_hours", Integer),
    Column("consensus", String),
    Column("timestamp", DateTime, default=func.now()),
    Column("status", String, default='active', nullable=False),
    Column("entry_timestamp", DateTime, nullable=True),
    Column("closed_timestamp", DateTime, nullable=True),
    # --- ВОТ НОВАЯ КОЛОНКА ---
    Column("is_high_quality", Boolean, default=False, nullable=False),
)
