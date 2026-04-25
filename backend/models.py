from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True)
    title = Column(Text, default="Untitled Lecture")
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    duration = Column(Float, nullable=True)
    audio_path = Column(Text, nullable=True)
    notes = Column(Text, default="")
    status = Column(Text, default="recorded")  # recorded | transcribing | transcribed

    tags = relationship("Tag", back_populates="lecture", cascade="all, delete-orphan")
    transcript = relationship("Transcript", back_populates="lecture", uselist=False, cascade="all, delete-orphan")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    name = Column(Text, nullable=False)
    time = Column(Float, nullable=False)
    char_index = Column(Integer, nullable=True)

    lecture = relationship("Lecture", back_populates="tags")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    content = Column(Text, default="")
    segments = Column(JSON, default=list)
    diarize = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    lecture = relationship("Lecture", back_populates="transcript")
