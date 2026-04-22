"""
presentation/api/middleware/audit_middleware.py — Middleware de auditoría.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from uuid import uuid4
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware que registra todas las solicitudes y respuestas."""
    
    async def dispatch(self, request: Request, call_next):
        # Generar ID de solicitud
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        # Obtener información de la solicitud
        method = request.method
        path = request.url.path
        client = request.client.host if request.client else "unknown"
        
        # Log de entrada
        logger.debug(f"[{request_id}] {method} {path} from {client}")
        
        # Procesar solicitud
        response = await call_next(request)
        
        # Log de salida
        logger.debug(f"[{request_id}] Response: {response.status_code}")
        
        return response
