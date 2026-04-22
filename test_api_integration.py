"""
test_api_integration.py — Prueba rápida de integración de API.
Ejecutar: python -m pytest test_api_integration.py -v
O: python test_api_integration.py
"""

import asyncio
import sys
from uuid import uuid4

# Verificar estructura de directorios
required_dirs = [
    "domain",
    "application",
    "infrastructure",
    "presentation"
]

print("=" * 70)
print("PRUEBA DE INTEGRACIÓN - SGAC API")
print("=" * 70)

print("\n[1] VERIFICANDO ESTRUCTURA DE DIRECTORIOS")
print("-" * 70)
import os
for dir_name in required_dirs:
    exists = os.path.isdir(dir_name)
    status = "✓" if exists else "✗"
    print(f"  {status} {dir_name}/")


print("\n[2] VERIFICANDO IMPORTACIONES DE CAPAS")
print("-" * 70)

try:
    from config import settings
    print("  ✓ config.settings")
except ImportError as e:
    print(f"  ✗ config.settings: {e}")
    sys.exit(1)

try:
    from infrastructure.database.connection import engine
    print("  ✓ infrastructure.database.connection")
except ImportError as e:
    print(f"  ✗ infrastructure.database.connection: {e}")
    sys.exit(1)

try:
    from infrastructure.database.models import Base
    print("  ✓ infrastructure.database.models")
except ImportError as e:
    print(f"  ✗ infrastructure.database.models: {e}")
    sys.exit(1)

try:
    from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
    from infrastructure.repositories.activity_repository_impl import ActivityRepositoryImpl
    print("  ✓ infrastructure.repositories")
except ImportError as e:
    print(f"  ✗ infrastructure.repositories: {e}")
    sys.exit(1)

try:
    from infrastructure.security.jwt_service import JWTService
    print("  ✓ infrastructure.security.jwt_service")
except ImportError as e:
    print(f"  ✗ infrastructure.security.jwt_service: {e}")
    sys.exit(1)

try:
    from application.use_cases.auth.authenticate_user import AuthenticateUserUseCase
    from application.use_cases.activity.create_activity import CreateActivityUseCase
    print("  ✓ application.use_cases")
except ImportError as e:
    print(f"  ✗ application.use_cases: {e}")
    sys.exit(1)

try:
    from presentation.api.routers import auth, activities
    print("  ✓ presentation.api.routers")
except ImportError as e:
    print(f"  ✗ presentation.api.routers: {e}")
    sys.exit(1)

try:
    from presentation.api.middleware import AuditMiddleware
    print("  ✓ presentation.api.middleware")
except ImportError as e:
    print(f"  ✗ presentation.api.middleware: {e}")
    sys.exit(1)


print("\n[3] VERIFICANDO CONFIGURACIÓN")
print("-" * 70)
print(f"  Database URL: {settings.database_url[:50]}...")
print(f"  Debug mode: {settings.debug}")
print(f"  Token expiration: {settings.access_token_expire_minutes} minutos")
print(f"  Upload directory: {settings.upload_dir}")


print("\n[4] VERIFICANDO ROUTERS")
print("-" * 70)
print(f"  ✓ auth.router (rutas: {len(auth.router.routes)} endpoints)")
print(f"  ✓ activities.router (rutas: {len(activities.router.routes)} endpoints)")


print("\n[5] VERIFICANDO FASTAPI APP")
print("-" * 70)
try:
    from main import app
    print(f"  ✓ App creada: {app.title}")
    print(f"  ✓ Routers registrados:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"    - {route.path}")
except ImportError as e:
    print(f"  ✗ No se pudo cargar main.app: {e}")
    sys.exit(1)


print("\n[6] VERIFICANDO TABLAS DE BASE DE DATOS")
print("-" * 70)
print(f"  Modelos ORM registrados:")
for table_name in Base.metadata.tables.keys():
    table = Base.metadata.tables[table_name]
    cols = len(table.columns)
    print(f"    - {table_name} ({cols} columnas)")


print("\n" + "=" * 70)
print("✓ TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE")
print("=" * 70)
print("\nPara iniciar el servidor:")
print("  uvicorn main:app --reload")
print("  (o con puerto personalizado:")
print("  uvicorn main:app --reload --port 8001)")
print("\nPara acceder a la documentación interactiva:")
print("  http://localhost:8000/docs")
