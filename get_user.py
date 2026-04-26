import asyncio
import sys
sys.path.append("c:\\sgac")
from infrastructure.database.connection import get_async_session
from sqlalchemy import text

async def main():
    async with get_async_session() as s:
        r = await s.execute(text('SELECT id FROM users LIMIT 1'))
        print(r.scalar())

asyncio.run(main())
