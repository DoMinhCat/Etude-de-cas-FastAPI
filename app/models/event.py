# TODO: modèle SQLAlchemy "Event" (timeline)
# - Lié à une Intervention et à une organisation.
# - Type d'évènement (enum libre), note/payload JSON, horodatage.
# - Index (intervention_id, created_at).

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.db.base import Base

class EventType(str, enum.Enum):
    CREATED = "created"
    STARTED = "started"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(Enum(EventType), nullable=False)
    note = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    intervention_id = Column(Integer, ForeignKey("interventions.id", ondelete="CASCADE"), nullable=False)
    organisation_id = Column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("technicians.id", ondelete="SET NULL"), nullable=True)

    intervention = relationship("Intervention", back_populates="events")
    organisation = relationship("Organisation", back_populates="events")
    created_by_technician = relationship("Technician", foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_event_intervention_created", "intervention_id", "created_at"),
    )

