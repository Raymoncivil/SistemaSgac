import asyncio
import sys
sys.path.append("c:\\sgac")
from infrastructure.database.connection import get_async_session
from sqlalchemy import text

async def main():
    async with get_async_session() as s:
        result = await s.execute(text('SELECT rut, full_name, role FROM users'))
        users = result.fetchall()
        print("Usuarios en BD:")
        for u in users:
            print(f"- RUT: {u.rut}, Nombre: {u.full_name}, Rol: {u.role}")

asyncio.run(main())
