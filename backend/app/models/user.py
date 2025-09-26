import uuid
import enum
from sqlalchemy import Column, String, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    investigator = "investigator"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(PgEnum(UserRole, name="userrole"), nullable=False)
