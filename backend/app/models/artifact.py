import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base_class import Base
from pgvector.sqlalchemy import Vector

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"))
    ufdr_file_id = Column(UUID(as_uuid=True), ForeignKey("ufdr_files.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(50))  # 'message', 'call', 'contact'
    extracted_text = Column(String)
    raw = Column(JSON)
    embedding = Column(Vector(384))  # 384 dims for all-MiniLM-L6-v2
    created_at = Column(DateTime, default=datetime.utcnow)