# app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.models.user import User
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings
from sqlalchemy import select
from app.schemas.user import UserCreate, UserRead
from app.core.security import get_password_hash
import uuid

router = APIRouter()

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    # 1. Get user from DB
    result = await db.execute(
        sa.select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # 2. Create token with role inside
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},  # 👈 here
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", response_model=UserRead)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    # 🚫 Block anyone trying to register as admin
    if user_in.role != "investigator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only register as an investigator. Admin accounts must be created internally."
        )

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = User(
        id=uuid.uuid4(),
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role="investigator",  # enforce default
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
