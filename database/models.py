"""
Database Models
===============

All database tables defined here with clear documentation.

Each model represents a table in PostgreSQL database.
All relationships and fields are clearly explained.

By OkayYouGotMe
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Base class for all models
Base = declarative_base()


# ============================================
# ENUMS (Predefined Options)
# ============================================

class MotivationStyle(enum.Enum):
    """
    How the user likes to be motivated.
    Affects tone of messages and assessments.
    """
    GENTLE = "gentle"          # Soft nudges, encouraging
    DIRECT = "direct"          # Brutally honest, straight talk
    CELEBRATE = "celebrate"    # Celebrate every win
    FACTUAL = "factual"        # Just the facts, no fluff


class TaskStatus(enum.Enum):
    """Current status of a task"""
    PENDING = "pending"             # Not started yet
    IN_PROGRESS = "in_progress"     # Currently working on it
    COMPLETED = "completed"         # Done!
    SKIPPED = "skipped"             # User chose to skip
    CANCELLED = "cancelled"         # No longer relevant


class TaskPriority(enum.Enum):
    """How urgent/important a task is"""
    LOW = "low"           # Can wait
    NORMAL = "normal"     # Standard priority
    HIGH = "high"         # Important
    URGENT = "urgent"     # Do ASAP


class ReminderPriority(enum.Enum):
    """
    How persistent reminders should be.
    Determines nagging frequency.
    """
    OPTIONAL = "optional"     # One reminder only
    NORMAL = "normal"         # 2 reminders
    IMPORTANT = "important"   # 3 reminders
    CRITICAL = "critical"     # Nag every 5 min until done


class ReminderStatus(enum.Enum):
    """Current state of a reminder"""
    PENDING = "pending"       # Waiting to send
    SENT = "sent"             # First reminder sent
    SNOOZED = "snoozed"       # User snoozed it
    COMPLETED = "completed"   # User confirmed completion
    CANCELLED = "cancelled"   # User cancelled it


# ============================================
# USER MODEL
# ============================================

class User(Base):
    """
    Represents a user of the AI Task Assistant.
    
    Each Telegram user gets one row in this table.
    Stores their profile, preferences, and settings.
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram info (unique identifier)
    telegram_chat_id = Column(String(50), unique=True, nullable=False, index=True)
    # Why index? We look up users by telegram_chat_id frequently
    
    # Basic info
    name = Column(String(100))
    profession = Column(String(200))
    work_schedule = Column(Text)  # Free-form text describing their schedule
    
    # Preferences
    timezone = Column(String(50), default="America/New_York")
    motivation_style = Column(SQLEnum(MotivationStyle), default=MotivationStyle.DIRECT)
    
    # Goals (stored as JSON array)
    # Example: ["Get promoted", "Save for house", "Stay healthy"]
    goals = Column(JSON, default=list)
    
    # Other preferences (stored as JSON object)
    # Example: {"hourly_checkins": true, "weekend_mode": false}
    preferences = Column(JSON, default=dict)
    
    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)  # Current step in onboarding
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships (links to other tables)
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    ideas = relationship("Idea", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', telegram_id='{self.telegram_chat_id}')>"


# ============================================
# TASK MODEL
# ============================================

class Task(Base):
    """
    Represents a task/to-do item for a user.
    
    Can be a standalone task or a subtask (parent_task_id set).
    """
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Link to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Task details
    task_name = Column(String(500), nullable=False)
    description = Column(Text)  # Optional longer description
    
    # Timing
    due_date = Column(DateTime)  # When it's due (optional)
    estimated_time = Column(Integer)  # Estimated minutes to complete
    
    # Status and priority
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.NORMAL)
    
    # Subtask support
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
    # If this is set, this task is a subtask of another task
    
    # Category (for organization)
    category = Column(String(100))  # Example: "Work", "Personal", "Health"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.task_name}', status='{self.status.value}')>"


# ============================================
# CONVERSATION MODEL
# ============================================

class Conversation(Base):
    """
    Stores conversation history between user and AI.
    
    Used for context in future responses.
    Limited to last N messages per user (see MAX_CONVERSATION_MEMORY).
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # The actual messages
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    
    # AI's understanding of the message
    intent = Column(String(100))  # Example: "add_task", "complete_task", "chat"
    context = Column(JSON)  # Additional context data
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, intent='{self.intent}', time='{self.timestamp}')>"


# ============================================
# REMINDER MODEL
# ============================================

class Reminder(Base):
    """
    Scheduled reminders for tasks.
    
    Supports persistent nagging based on priority level.
    """
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    # task_id can be null for general reminders not tied to tasks
    
    # When to remind
    reminder_time = Column(DateTime, nullable=False, index=True)
    
    # How persistent to be
    priority = Column(SQLEnum(ReminderPriority), default=ReminderPriority.NORMAL)
    
    # Status tracking
    status = Column(SQLEnum(ReminderStatus), default=ReminderStatus.PENDING, index=True)
    nag_count = Column(Integer, default=0)  # How many times we've nagged
    
    # Snooze support
    snoozed_until = Column(DateTime)  # If snoozed, when to remind again
    
    # Message to show when reminding
    reminder_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    task = relationship("Task", back_populates="reminders")
    
    def __repr__(self):
        return f"<Reminder(id={self.id}, time='{self.reminder_time}', priority='{self.priority.value}')>"


# ============================================
# IDEA MODEL (OTR - Off The Record)
# ============================================

class Idea(Base):
    """
    Stores user's ideas, notes, and thoughts (OTR).
    
    These are things users want to remember but aren't tasks yet.
    """
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # The idea itself
    idea_text = Column(Text, nullable=False)
    
    # Organization
    category = Column(String(100), index=True)  # Auto-categorized by AI
    notes = Column(Text)  # Optional additional notes
    
    # Status
    archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="ideas")
    
    def __repr__(self):
        return f"<Idea(id={self.id}, category='{self.category}', archived={self.archived})>"


# ============================================
# ASSESSMENT MODEL
# ============================================

class Assessment(Base):
    """
    Stores periodic assessments (daily, weekly, monthly, quarterly).
    
    These are the brutal honest reviews of user's productivity.
    """
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Type and period
    assessment_type = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metrics
    tasks_completed = Column(Integer, default=0)
    tasks_planned = Column(Integer, default=0)
    completion_rate = Column(Integer)  # Percentage (0-100)
    
    # The actual assessment text
    assessment_text = Column(Text, nullable=False)
    
    # Score (0-10)
    score = Column(Integer)
    
    # Patterns detected
    patterns = Column(JSON)  # Example: {"procrastination_trigger": "patient_charts"}
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="assessments")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, type='{self.assessment_type}', score={self.score})>"


# ============================================
# COMPLETION MODEL (For Stats)
# ============================================

class Completion(Base):
    """
    Tracks when tasks are completed.
    
    Used for generating statistics and assessments.
    Separate from Task model to preserve history even if tasks are deleted.
    """
    __tablename__ = "completions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(Integer)  # Reference to task (might be deleted later)
    
    # Task details (snapshot at time of completion)
    task_name = Column(String(500))
    category = Column(String(100))
    priority = Column(String(20))
    
    # Timing
    completed_at = Column(DateTime, default=datetime.utcnow, index=True)
    time_taken = Column(Integer)  # Actual minutes spent (if tracked)
    
    # Was it on time?
    was_on_time = Column(Boolean)  # Did they complete before due_date?
    
    # No explicit relationship to preserve data even if task is deleted
    
    def __repr__(self):
        return f"<Completion(id={self.id}, task='{self.task_name}', completed='{self.completed_at}')>"


# ============================================
# HELPER FUNCTION
# ============================================

def create_all_tables(engine):
    """
    Create all database tables.
    
    Run this once when setting up the database for the first time.
    
    Args:
        engine: SQLAlchemy database engine
    """
    Base.metadata.create_all(engine)
    print("✅ All database tables created successfully!")


def drop_all_tables(engine):
    """
    Drop all database tables (DANGEROUS!).
    
    Only use for development/testing.
    All data will be lost!
    
    Args:
        engine: SQLAlchemy database engine
    """
    Base.metadata.drop_all(engine)
    print("⚠️  All database tables dropped!")
