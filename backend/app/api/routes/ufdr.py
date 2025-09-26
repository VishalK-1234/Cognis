# app/api/routes/ufdr.py
import os
import hashlib
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.models.ufdrfile import UFDRFile   # <-- import model directly
from app.models.artifact import Artifact   # <-- import model directly

# ... rest of file unchanged


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/ufdr", tags=["UFDR"])

def sha256sum_from_path(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

async def save_upload_file(upload_file: UploadFile, dest_path: str):
    # Save streamed content to disk
    contents = await upload_file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

@router.post("/upload")
async def upload_ufdr(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Basic filename sanitization (simple)
    filename = file.filename.replace("/", "_").replace("\\", "_")
    unique_suffix = uuid.uuid4().hex[:8]
    stored_filename = f"{unique_suffix}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    # Save file to disk
    await save_upload_file(file, file_path)

    # Compute SHA256
    file_hash = sha256sum_from_path(file_path)

    # Check duplicates by hash
    result = await db.execute(
        select(UFDRFile).where(UFDRFile.meta.op("->>")("hash") == file_hash)
    )
    existing = result.scalars().first()
    if existing:
        # Remove saved duplicate file
        try:
            os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File already uploaded (same hash)")

    # Create DB record for UFDRFile
    ufdr = UFDRFile(
        case_id=None,
        filename=filename,
        storage_path=file_path,
        meta={"hash": file_hash},
        uploaded_at=datetime.utcnow()
    )
    db.add(ufdr)
    await db.commit()
    await db.refresh(ufdr)

    # Create a few demo artifacts so endpoints have data immediately
    demo_texts = [
        f"Extracted message sample for {filename}: phone number +91-99999xxxx",
        f"Contact entry found in {filename}: John Doe, +1-555-0123",
        f"Log snippet from {filename}: login at 2025-09-01T12:00:00Z"
    ]
    demo_types = ["message", "contact", "log"]

    created_artifact_ids = []
    for t, txt in zip(demo_types, demo_texts):
        art = Artifact(
            case_id=None,
            ufdr_file_id=ufdr.id,
            type=t,
            extracted_text=txt,
            raw={"demo": True},
            # embedding left null for now; pgvector accepts None
            created_at=datetime.utcnow()
        )
        db.add(art)
        await db.flush()  # get PK populated (SQLAlchemy)
        created_artifact_ids.append(str(art.id))

    await db.commit()

    return {
        "id": str(ufdr.id),
        "filename": ufdr.filename,
        "hash": file_hash,
        "uploaded_at": ufdr.uploaded_at.isoformat(),
        "demo_artifact_ids": created_artifact_ids,
    }
