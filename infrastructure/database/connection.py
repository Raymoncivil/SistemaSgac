"""
infrastructure/database/connection.py — Conexión async SQLAlchemy.
Usa DATABASE_URL desde config (.env) conforme a SGAC.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

DATABASE_URL = settings.database_url
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


def get_async_session() -> AsyncSession:
    """Crea y retorna una sesión async de SQLAlchemy."""
    return AsyncSessionLocal()
