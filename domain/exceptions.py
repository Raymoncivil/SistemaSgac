"""
domain/exceptions.py — Excepciones personalizadas de dominio.
No dependen de ninguna librería externa (sin FastAPI, SQLAlchemy).
"""


class DomainException(Exception):
    """Excepción base de dominio."""
    pass


class InvalidRUTException(DomainException):
    """RUT chileno inválido."""
    pass


class ActivityNotFoundError(DomainException):
    """Actividad no encontrada."""
    pass


class UserNotFoundError(DomainException):
    """Usuario no encontrado."""
    pass


class UnauthorizedAccessError(DomainException):
    """Acceso no autorizado."""
    pass


class InvalidTokenError(DomainException):
    """Token JWT inválido o expirado."""
    pass


class InvalidEmailError(DomainException):
    """Email inválido."""
    pass


class ValidationError(DomainException):
    """Error de validación de datos."""
    pass
