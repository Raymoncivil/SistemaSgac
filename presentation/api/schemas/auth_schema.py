"""
presentation/api/schemas/auth_schema.py — Esquemas Pydantic para autenticación.
"""

from pydantic import BaseModel, Field


class LoginRequestSchema(BaseModel):
    rut: str = Field(..., title="RUT chileno", example="12345678-9")
    password: str = Field(..., min_length=6, title="Contraseña")


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    rut: str
    full_name: str
    role: str


class LogoutResponseSchema(BaseModel):
    message: str
