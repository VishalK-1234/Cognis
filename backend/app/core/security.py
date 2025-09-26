# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, List

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import get_db_session

# ---- Password hashing ----
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plaintext password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---- OAuth2 scheme ----
# tokenUrl should point to the login endpoint that returns the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---- JWT helpers ----
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token. `data` must include whatever you want to be present in the token
    (we expect at least {"sub": "<user id>", "role": "<user-role>"}).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta is not None else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate the JWT. Raises 401 HTTPException on failure.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# ---- Current user dependency ----
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Resolve the current user from the token 'sub' claim.
    NOTE: User model is imported locally here to avoid circular imports at module import time.
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user id (sub)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Local import to avoid circular import problems
    from app.models.user import User  # imported here on purpose

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ---- RBAC helpers ----
def require_role(*roles: str) -> Callable:
    """
    Returns a FastAPI dependency that ensures the current user's role is in `roles`.
    Usage:
        @router.get("/some")
        async def some_route(current_user = Depends(require_role("admin"))):
            ...
    """
    async def role_dependency(current_user = Depends(get_current_user)):
        # `role` might be stored as enum/str on the model — compare strings
        user_role = getattr(current_user, "role", None)
        if user_role is None or str(user_role) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted",
            )
        return current_user
    return role_dependency


# convenience pre-made dependencies
require_investigator = require_role("investigator")
require_admin = require_role("admin")
require_investigator_or_admin = require_role("investigator", "admin")
