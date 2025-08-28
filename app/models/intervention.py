# TODO: modèle SQLAlchemy "Intervention" 
# - Lié à un Client et à une organisation.
# - Statut (enum libre ou texte + CHECK), timestamps, etc.

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base

class InterventionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(Enum(InterventionStatus), nullable=False, default=InterventionStatus.PENDING)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    organisation_id = Column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    technician_id = Column(Integer, ForeignKey("technicians.id", ondelete="RESTRICT"), nullable=False)

    client = relationship("Client", back_populates="interventions")
    organisation = relationship("Organisation", back_populates="interventions")
    technician = relationship("Technician", back_populates="interventions")
    events = relationship("Event", back_populates="intervention", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_intervention_client_created", "client_id", "created_at"),
    )