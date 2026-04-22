"""
presentation/api/middleware — Middleware de FastAPI.
"""

from presentation.api.middleware.audit_middleware import AuditMiddleware

__all__ = ["AuditMiddleware"]
