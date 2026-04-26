"""
presentation/api/schemas/auth_schema.py — Esquemas Pydantic para autenticación.
"""

from pydantic import BaseModel, Field


# =========================
# LOGIN
# =========================

class LoginRequestSchema(BaseModel):
    rut: str = Field(..., title="RUT chileno", example="12345678-9")
    password: str = Field(..., min_length=8, title="Contraseña")  # 🔥 corregido


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    rut: str
    full_name: str
    role: str


# =========================
# REGISTER 🔥
# =========================

class RegisterRequestSchema(BaseModel):
    rut: str = Field(..., example="12345678-9")
    full_name: str = Field(..., example="Juan Pérez")
    password: str = Field(..., min_length=8)
    role: str = Field(..., example="user")  # user / admin


class RegisterResponseSchema(BaseModel):
    user_id: str
    rut: str
    full_name: str
    role: str


# =========================
# LOGOUT
# =========================

class LogoutResponseSchema(BaseModel):
    message: str