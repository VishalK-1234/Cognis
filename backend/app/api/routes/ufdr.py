from fastapi import APIRouter, UploadFile, File, Depends
from app.core.security import get_current_user

router = APIRouter(prefix="/ufdr", tags=["UFDR"])

@router.post("/upload")
async def upload_ufdr(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    return {"filename": file.filename, "message": "File received (stub)"}
