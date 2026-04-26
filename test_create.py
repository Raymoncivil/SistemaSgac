"""
Test PASO 5: inserta una actividad real en la BD.
Ejecutar: .venv\Scripts\python.exe test_create.py
"""
import asyncio
import sys
import traceback
sys.path.insert(0, r"C:\sgac")

async def main():
    from uuid import uuid4
    from datetime import datetime, timezone
    from infrastructure.database.connection import AsyncSessionLocal, engine
    from infrastructure.repositories.activity_repository_impl import ActivityRepositoryImpl
    from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
    from application.use_cases.activity.create_activity import CreateActivityUseCase
    from application.dtos.activity_dto import ActivityCreateDTO

    print("=== Buscando un usuario existente en BD ===")
    async with AsyncSessionLocal() as session:
        from sqlalchemy import text
        result = await session.execute(text("SELECT id FROM users LIMIT 1"))
        row = result.fetchone()
        if not row:
            print("  ERROR: No hay usuarios en la BD. Crea un usuario primero.")
            return
        user_id = row[0]
        print(f"  Usuario encontrado: {user_id}")

    print("\n=== Intentando crear actividad en BD ===")
    async with AsyncSessionLocal() as session:
        try:
            activity_repo = ActivityRepositoryImpl(session)
            user_repo = UserRepositoryImpl(session)
            use_case = CreateActivityUseCase(activity_repo, user_repo)

            dto = ActivityCreateDTO(
                day_of_april=10,
                title="Test actividad desde script",
                priority_id=2,
                description="Prueba directa a BD",
                emoji="📅",
                checklist=[],
                image_path=None,
            )

            from uuid import UUID
            result = await use_case.execute(UUID(str(user_id)), dto)
            print(f"  OK - Actividad creada con id={result.id}, titulo={result.title}")
        except Exception as e:
            print(f"  ERROR al crear en BD: {type(e).__name__}: {e}")
            traceback.print_exc()

asyncio.run(main())
