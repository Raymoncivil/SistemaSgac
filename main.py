from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from presentation.api.routers import auth, activities, admin
from infrastructure.database.connection import engine
from infrastructure.database.models import Base
from domain.exceptions import DomainException
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida de la aplicación FastAPI.
    - Startup: crea tablas
    - Shutdown: cierra la conexión
    """
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tablas de base de datos creadas/verificadas")
    
    yield
    
    # Shutdown
    await engine.dispose()
    print("✓ Conexión a base de datos cerrada")


app = FastAPI(
    title="Sistema de Gestión de Actividades",
    version="1.0.0",
    description="Sistema para gestionar actividades de abril con calendarios",
    lifespan=lifespan
)

# CORS - Solo orígenes confiables
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=[],
    max_age=600,
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

UPLOADS_DIR = Path(settings.upload_dir).resolve()
if UPLOADS_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


@app.exception_handler(DomainException)
async def domain_exception_handler(_, exc: DomainException):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.get("/")
def read_root():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Bienvenido al Sistema de Gestión de Actividades", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "SGAC API"}