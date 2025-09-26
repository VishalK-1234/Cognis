# app/api/routes/audit.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.models.auditlog import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs")
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50))
    logs = result.scalars().all()

    return [
        {
            "id": str(l.id),
            "method": l.method,
            "path": l.path,
            "status_code": l.status_code,
            "timestamp": l.timestamp,
            "user_agent": l.user_agent,
        }
        for l in logs
    ]
