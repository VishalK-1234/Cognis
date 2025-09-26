# app/api/routes/conversation.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.db.deps import get_db
from app.core.security import get_current_user
from app.models.artifact import Artifact
from app.models.ufdrfile import UFDRFile
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["Conversation"])

@router.get("/conv/{ufdr_file_id}")
async def conv_query(
    ufdr_file_id: str,
    q: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=25),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ensure file exists
    result = await db.execute(select(UFDRFile).where(UFDRFile.id == ufdr_file_id))
    ufdr = result.scalars().first()
    if not ufdr:
        raise HTTPException(status_code=404, detail="UFDR file not found")

    # simple keyword search: look for artifacts containing any query terms (case-insensitive)
    q_terms = [t.strip() for t in q.split() if t.strip()]
    if not q_terms:
        raise HTTPException(status_code=400, detail="Empty query after tokenization")

    # build OR-like ilike conditions for terms against extracted_text
    conds = [Artifact.extracted_text.ilike(f"%{term}%") for term in q_terms]
    stmt = select(Artifact).where(Artifact.ufdr_file_id == ufdr_file_id).where(or_(*conds)).limit(limit)
    result = await db.execute(stmt)
    matches = result.scalars().all()

    # If no matches, fallback: return top few artifacts for context
    if not matches:
        stmt2 = select(Artifact).where(Artifact.ufdr_file_id == ufdr_file_id).limit(limit)
        result2 = await db.execute(stmt2)
        matches = result2.scalars().all()

    # Build a simple response by concatenating extracts (trim for size)
    snippets = []
    for a in matches:
        text = (a.extracted_text or "")[:800]  # limit snippet length
        snippets.append(f"[{a.type}] {text}")

    # Simple synthesis: echo query and include matched snippets
    answer = f"I searched the UFDR file for: '{q}'.\nFound {len(snippets)} relevant artifacts:\n\n" + "\n\n".join(snippets)

    return {
        "query": q,
        "ufdr_file_id": ufdr_file_id,
        "answer": answer,
        "num_matches": len(snippets),
    }
