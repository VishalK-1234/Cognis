# app/api/v1/endpoints/cases.py

from fastapi import APIRouter, Depends
from app.core.deps import require_role, TokenData

router = APIRouter()

@router.get("/cases")
def list_cases(current_user: TokenData = Depends(require_role(["investigator", "admin"]))):
    return {"message": f"Hello {current_user.role}, here are the cases."}

@router.delete("/cases/{case_id}")
def delete_case(case_id: str, current_user: TokenData = Depends(require_role(["admin"]))):
    return {"message": f"Case {case_id} deleted by admin."}
