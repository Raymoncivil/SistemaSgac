import asyncio
from infrastructure.database.connection import engine
from sqlalchemy import text

async def alter_table():
    async with engine.begin() as conn:
        print("Agregando columna 'time' a activities...")
        await conn.execute(text('ALTER TABLE activities ADD COLUMN "time" VARCHAR(5);'))
        print("Columna agregada exitosamente.")

if __name__ == "__main__":
    asyncio.run(alter_table())
