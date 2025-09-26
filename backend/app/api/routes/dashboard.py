# app/api/routes/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func   # ✅ FIXED

from app.db.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.ufdrfile import UFDRFile
from app.models.artifact import Artifact

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_users = await db.scalar(select(func.count(User.id)))
    total_files = await db.scalar(select(func.count(UFDRFile.id)))
    total_artifacts = await db.scalar(select(func.count(Artifact.id)))

    result = await db.execute(select(UFDRFile).order_by(UFDRFile.uploaded_at.desc()).limit(5))
    recent = result.scalars().all()

    return {
        "total_users": total_users,
        "total_ufdr_files": total_files,
        "total_artifacts": total_artifacts,
        "recent_uploads": [
            {"filename": f.filename, "uploaded_at": f.uploaded_at} for f in recent
        ],
    }
