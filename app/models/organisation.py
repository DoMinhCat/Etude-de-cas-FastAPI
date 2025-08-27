from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    street = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)

    technicians = relationship("Technician", back_populates="organisation", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="organisation", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="organisation", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="organisation", cascade="all, delete-orphan")
