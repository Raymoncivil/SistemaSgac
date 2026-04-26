"""
config.py — Configuración centralizada usando Pydantic Settings.
Respeta las dependencias hacia adentro de Clean Architecture.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Las variables se cargan desde .env y variables de entorno.
    """

    # Database
    database_url: str = Field(..., description="URL de conexión a PostgreSQL")

    # Security
    secret_key: str = Field(..., description="Clave secreta para JWT")
    access_token_expire_minutes: int = 30    # ← sin Field(), valor fijo
    algorithm: str = "HS256"

    # Storage
    upload_dir: str = "uploads/"

    # Environment
    debug: bool = True
    allowed_origins: list = [
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value.strip()) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return value.strip()

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"        # ← ignora variables del .env no declaradas
    }


# Instancia global
settings = Settings()
