from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean
from sqlalchemy.sql import func
from database.database import Base

import uuid


class User(Base):
    __tablename__ = 'users'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    tusername = Column(String, nullable=False, unique=True)
    tid = Column(BigInteger, nullable=False, unique=True)
    role = Column(String, nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    end_message_sended = Column(Boolean, nullable=False, default=False)
    chat_id = Column(BigInteger, nullable=True)


class Lesson(Base):
    __tablename__ = 'lessons'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    chat_id = Column(BigInteger, nullable=False)
    title = Column(String, nullable=False)
    content_message_id = Column(BigInteger, nullable=False)
    archived = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserLessonProgress(Base):
    __tablename__ = 'user_lesson_progress'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_uid = Column(String, nullable=False)
    at_lesson_uid = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Setting(Base):
    __tablename__ = 'settings'

    key = Column(String, primary_key=True, nullable=False)
    value = Column(String, nullable=False)


class LessonContent(Base):
    __tablename__ = 'lesson_contents'

    uid = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    lesson_uid = Column(String, nullable=False)
    message_id = Column(BigInteger, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    # New fields to support multiple content types
    content_type = Column(String, nullable=False, default='message')  # e.g. 'text','photo','document','audio','video','url','message'
    file_id = Column(String, nullable=True)  # Telegram file_id (if stored)
    file_path = Column(String, nullable=True)  # Local path (optional)
    text = Column(String, nullable=True)  # For text content
    url = Column(String, nullable=True)  # For URL content
    metadata_json = Column(String, nullable=True)  # JSON string with extra metadata like duration, thumb, etc.
