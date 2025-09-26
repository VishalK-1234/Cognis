#backend/app/middleware/audit.py

from starlette.middleware.base import BaseHTTPMiddleware
from app.db.session import get_db_session
from app.models.auditlog import AuditLog
import uuid
from datetime import datetime

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        async with get_db_session() as db:  # ✅ works now
            log = AuditLog(
                id=uuid.uuid4(),
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                timestamp=datetime.utcnow(),
                user_agent=request.headers.get("user-agent"),
            )
            db.add(log)
            await db.commit()

        return response
