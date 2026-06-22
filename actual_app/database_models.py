from actual_app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)

    tasks = relationship('Task', back_populates='owner')

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_completed = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', back_populates='tasks')

    attachments = relationship("TaskFile", back_populates="task", cascade="all, delete-orphan")

class TaskFile(Base):
    __tablename__ = "task_files"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    task = relationship("Task", back_populates="attachments")