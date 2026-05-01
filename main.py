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