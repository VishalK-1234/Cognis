from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    investigator = "investigator"
    admin = "admin"

class User(Base):
    __tablename__ = "users"   # ✅ important (not "user")

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.investigator, nullable=False)  # ✅