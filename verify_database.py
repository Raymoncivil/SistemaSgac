"""
verify_database.py — Verifica la conexión y estructura de la BD.
Ejecutar: python verify_database.py
"""

import asyncio
from config import settings
from infrastructure.database.connection import engine
from infrastructure.database.models import Base


async def verify_connection():
    """Verifica la conexión a PostgreSQL."""
    print("=" * 60)
    print("VERIFICADOR DE BASE DE DATOS - SGAC")
    print("=" * 60)
    
    # 1. Mostrar configuración
    print("\n[1] CONFIGURACIÓN DE CONEXIÓN")
    print(f"URL: {settings.database_url}")
    print(f"Debug: {settings.debug}")
    
    # 2. Intentar conectar
    print("\n[2] INTENTANDO CONECTAR...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✓ Conexión exitosa a PostgreSQL")
            print(f"  Versión: {version}")
    except Exception as e:
        print(f"✗ Error de conexión: {str(e)}")
        print("\nSolución:")
        print("1. Verifica que PostgreSQL esté ejecutándose")
        print("2. Verifica el usuario y contraseña en .env")
        print("3. Verifica que la BD 'mi_app' exista")
        print("   Crea con: psql -U postgres -c 'CREATE DATABASE mi_app;'")
        return
    
    # 3. Mostrar tablas que se crearán
    print("\n[3] TABLAS A CREAR")
    print("-" * 60)
    for table in Base.metadata.tables.values():
        print(f"\nTabla: {table.name}")
        print(f"  Columnas:")
        for col in table.columns:
            col_type = str(col.type)
            nullable = "NULL" if col.nullable else "NOT NULL"
            primary = " (PRIMARY KEY)" if col.primary_key else ""
            print(f"    - {col.name}: {col_type} {nullable}{primary}")
    
    # 4. Crear tablas
    print("\n[4] CREANDO TABLAS...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✓ Tablas creadas exitosamente")
    except Exception as e:
        print(f"✗ Error al crear tablas: {str(e)}")
        return
    
    # 5. Verificar contenido
    print("\n[5] RESUMEN DE BASE DE DATOS")
    print("-" * 60)
    try:
        async with engine.begin() as conn:
            for table_name in ["users", "activities", "audit_logs"]:
                result = await conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = result.scalar()
                print(f"  {table_name}: {count} registros")
    except Exception as e:
        print(f"  Error al contar: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✓ VERIFICACIÓN COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verify_connection())
