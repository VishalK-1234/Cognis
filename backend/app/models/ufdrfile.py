import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base_class import Base

class UFDRFile(Base):
    __tablename__ = "ufdr_files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"))
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    meta = Column(JSON)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
