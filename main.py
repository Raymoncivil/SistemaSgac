from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import traceback
import logging

# ── Silenciar logs SQL verbose de SQLAlchemy (solo mostrar WARNING+) ──────────
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
# ─────────────────────────────────────────────────────────────────────────────

from presentation.api.routers import auth, activities, admin
from infrastructure.database.connection import engine
from infrastructure.database.models import Base
from config import settings

from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migración automática para agregar la columna 'time'
        try:
            await conn.execute(text('ALTER TABLE activities ADD COLUMN "time" VARCHAR(5);'))
            print("[SGAC] Migración: Columna 'time' agregada exitosamente.")
        except Exception as e:
            # Si falla es probable que la columna ya exista, lo ignoramos silenciosamente
            pass
            
    # NUEVO BLOQUE DE CONEXIÓN PARA EVITAR InFailedSQLTransactionError
    async with engine.begin() as conn2:
        # INSERTAR USUARIOS DE PRUEBA SI NO EXISTEN
        try:
            from infrastructure.security.jwt_service import JWTService
            from uuid import uuid4
            from datetime import datetime
            
            auth_svc = JWTService()
            
            # Verificar si existe el admin 111111111
            admin_check = await conn2.execute(text("SELECT id FROM users WHERE rut = '111111111'"))
            if not admin_check.fetchone():
                pwd_admin = auth_svc.hash_password("admin123")
                await conn2.execute(
                    text("INSERT INTO users (id, rut, full_name, password_hash, role, is_active, created_at) VALUES (:id, :rut, :name, :pwd, :role, True, :dt)"),
                    {"id": str(uuid4()), "rut": "111111111", "name": "Admin de Prueba", "pwd": pwd_admin, "role": "admin", "dt": datetime.now()}
                )
            
            # Verificar si existe el user 222222222
            user_check = await conn2.execute(text("SELECT id FROM users WHERE rut = '222222222'"))
            pwd_user = auth_svc.hash_password("usuario123")
            if not user_check.fetchone():
                await conn2.execute(
                    text("INSERT INTO users (id, rut, full_name, password_hash, role, is_active, created_at) VALUES (:id, :rut, :name, :pwd, :role, True, :dt)"),
                    {"id": str(uuid4()), "rut": "222222222", "name": "Usuario Normal", "pwd": pwd_user, "role": "user", "dt": datetime.now()}
                )
            else:
                await conn2.execute(text("UPDATE users SET password_hash = :pwd WHERE rut = '222222222'"), {"pwd": pwd_user})
            print("[SGAC] Usuarios de prueba verificados/creados.")
        except Exception as e:
            print(f"[SGAC] Error creando usuarios de prueba: {e}")
            
    print("[OK] Servidor listo")
    yield
    await engine.dispose()

app = FastAPI(title="SGAC", lifespan=lifespan)

# CORRECCIÓN DE CORS: No puede ser "*" si credentials es True
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(activities.router, prefix="/api/activities")
app.include_router(admin.router, prefix="/api/admin")

ROOT = Path(__file__).resolve().parent
app.mount("/frontend", StaticFiles(directory=str(ROOT / "frontend"), html=True))

@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    print(f"ERROR: {exc}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

@app.get("/")
async def root():
    return FileResponse(str(ROOT / "frontend" / "index.html"))