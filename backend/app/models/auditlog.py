from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.base_class import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method = Column(String(10), nullable=False)            # GET/POST/PUT/DELETE
    path = Column(String, nullable=False)                  # /api/v1/...
    status_code = Column(Integer, nullable=False)          # 200, 404, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)  # time of request
    user_agent = Column(String, nullable=True)             # browser or client info
