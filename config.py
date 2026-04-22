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
    Todas son validadas por Pydantic automáticamente.
    """
    
    # Database
    database_url: str = Field(..., description="URL de conexión a PostgreSQL")
    
    # Security
    secret_key: str = Field(..., description="Clave secreta para JWT")
    access_token_expire_minutes: int = Field(
        default=1,
        description="Expiración del token JWT en minutos"
    )
    algorithm: str = Field(default="HS256", description="Algoritmo para JWT")
    
    # Storage
    upload_dir: str = Field(
        default="uploads/",
        description="Directorio para almacenamiento de imágenes"
    )
    
    # Environment
    debug: bool = Field(
        default=True,
        description="Modo debug"
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:8000", "http://127.0.0.1:8000"],
        description="Orígenes de frontend confiables para CORS"
    )

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("Solo se permite HS256 para JWT")
        return value

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value.strip()) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return value.strip()

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
    
    class Config:
        """
        Configuración de Pydantic.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
