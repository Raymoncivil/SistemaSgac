from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings

DATABASE_URL = settings.database_url  # ej: "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session