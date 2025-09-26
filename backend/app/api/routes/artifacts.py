# app/api/routes/artifacts.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.db.deps import get_db
from app.core.security import get_current_user
from app.models.artifact import Artifact
from app.models.ufdrfile import UFDRFile
from app.models.user import User

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])

@router.get("/list/{ufdr_file_id}")
async def list_artifacts(
    ufdr_file_id: str,
    q: str | None = Query(None, description="Optional keyword to filter artifacts"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ensure UFDR file exists
    result = await db.execute(select(UFDRFile).where(UFDRFile.id == ufdr_file_id))
    ufdr = result.scalars().first()
    if not ufdr:
        raise HTTPException(status_code=404, detail="UFDR file not found")

    # authorization: allow admin or uploader only
    if getattr(current_user, "role", None) != "admin":
        # uploaded_by may be stored in meta or separate column; if not present, skip strict check
        uploaded_by = ufdr.meta.get("uploaded_by") if isinstance(ufdr.meta, dict) else None
        if uploaded_by:
            from uuid import UUID
            try:
                if str(uploaded_by) != str(current_user.id):
                    raise HTTPException(status_code=403, detail="Not authorized")
            except Exception:
                pass

    # fetch artifacts; optionally filter by keyword in extracted_text
    stmt = select(Artifact).where(Artifact.ufdr_file_id == ufdr_file_id)
    if q:
        q_like = f"%{q}%"
        stmt = stmt.where(Artifact.extracted_text.ilike(q_like))

    result = await db.execute(stmt)
    arts = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "type": a.type,
            "extracted_text": a.extracted_text,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "ufdr_file_id": str(a.ufdr_file_id) if a.ufdr_file_id else None,
        }
        for a in arts
    ]
