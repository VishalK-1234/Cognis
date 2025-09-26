from app.db.base_class import Base

# Import all models so Alembic can see them
from app.models.user import User
from app.models.case import Case
from app.models.ufdrfile import UFDRFile
from app.models.artifact import Artifact
from app.models.auditlog import AuditLog
