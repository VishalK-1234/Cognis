# backend/app/api/routes/cases.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.deps import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.case import Case

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("/create", status_code=201)
async def create_case(case_name: str,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only admin users can create cases")
    new_case = Case(title=case_name, created_by=current_user.id)
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    return {"id": str(new_case.id), "title": new_case.title, "created_by": str(new_case.created_by)}

@router.get("/list")
async def list_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = await db.execute(select(Case).order_by(Case.created_at.desc()))
    cases = q.scalars().all()
    out = [
        {
            "id": str(c.id),
            "title": c.title,
            "description": c.description,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "created_by": str(c.created_by) if c.created_by else None,
        }
        for c in cases
    ]
    return out
