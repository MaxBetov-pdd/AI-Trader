from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKey, func

# URL теперь указывает на использование асинхронного драйвера aiosqlite
DATABASE_URL = "sqlite+aiosqlite:///./trader_history.db"

# Создаем асинхронный движок
async_engine = create_async_engine(DATABASE_URL)

# Создаем фабрику для асинхронных сессий
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
)
