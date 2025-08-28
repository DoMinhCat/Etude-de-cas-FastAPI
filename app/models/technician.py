# TODO: modèle SQLAlchemy "Technician"
# - Rattaché à une organisation (org_id).
# - Unicité éventuelle (email/org).

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base

class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc)) 

    org_id = Column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)

    organisation = relationship("Organisation", back_populates="technicians")
    interventions = relationship("Intervention", back_populates="technician", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint("email", "org_id", name="uq_technician_email_org"),
    )
