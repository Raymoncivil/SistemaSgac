import asyncio
from sqlalchemy.future import select
from infrastructure.database.database import SessionLocal
from infrastructure.database.models import ActivityModel

async def run():
    async with SessionLocal() as db:
        result = await db.execute(select(ActivityModel))
        activities = result.scalars().all()
        for a in activities:
            print(a.id, a.title, a.description, a.emoji, a.checklist)

if __name__ == "__main__":
    asyncio.run(run())
