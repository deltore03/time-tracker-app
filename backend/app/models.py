from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class User(Base):
	__tablename__ = "users"
	
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, index=True, nullable=False)
	password_hash = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

	time_entries = relationship("TimeEntry", back_populates="user")

class TimeEntry(Base):
	__tablename__ = "time_entries"
	
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	clock_in = Column(DateTime, nullable=False)
	clock_out = Column(String, nullable=True)
	total_hours = Column(String, nullable=True)
	date = Column(String, nullable=False)
	
	user = relationship("User", back_populates="time_entries")
