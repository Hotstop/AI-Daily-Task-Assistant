"""
Database Operations
===================

All database functions in one place - clean and simple.

Every function is clearly documented and easy to understand.
No complex queries hidden in other files - everything is here.

By OkayYouGotMe
"""

from sqlalchemy import create_engine, and_, or_, desc
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging

from .models import (
    User, Task, Conversation, Reminder, Idea, 
    Assessment, Completion, Base,
    MotivationStyle, TaskStatus, TaskPriority,
    ReminderPriority, ReminderStatus
)
from config.settings import DATABASE_URL, MAX_CONVERSATION_MEMORY

# Set up logging
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create scoped session factory for thread-safe sessions
from sqlalchemy.orm import scoped_session
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_database():
    """
    Initialize database - create all tables.
    
    Run this once when setting up the application.
    Safe to run multiple times (won't recreate existing tables).
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def get_db() -> Session:
    """
    Get a database session.
    
    Use this in a with statement for automatic cleanup:
        with get_db() as db:
            # do database stuff
    
    Returns:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# USER OPERATIONS
# ============================================

def create_user(telegram_chat_id: str, name: str = None) -> Optional[User]:
    """
    Create a new user in the database.
    
    Args:
        telegram_chat_id: User's Telegram chat ID (unique)
        name: User's name (optional)
    
    Returns:
        Created User object, or None if failed
    """
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(
            User.telegram_chat_id == telegram_chat_id
        ).first()
        
        if existing:
            logger.info(f"User {telegram_chat_id} already exists")
            db.refresh(existing)
            db.expunge(existing)
            return existing
        
        # Create new user
        user = User(
            telegram_chat_id=telegram_chat_id,
            name=name,
            onboarding_completed=False,
            onboarding_step=0
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)  # Detach from session
        
        logger.info(f"✅ Created new user: {telegram_chat_id}")
        return user
        
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}")
        db.rollback()
        return None
    finally:
        SessionLocal.remove()


def get_user_by_telegram_id(telegram_chat_id: str) -> Optional[User]:
    """
    Get user by their Telegram chat ID.
    
    This is how we identify users when they send messages.
    
    Args:
        telegram_chat_id: User's Telegram chat ID
    
    Returns:
        User object or None if not found
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.telegram_chat_id == telegram_chat_id
        ).first()
        
        if user:
            # Update last active time
            user.last_active = datetime.utcnow()
            db.commit()
            db.refresh(user)
            # Make object usable outside session
            db.expunge(user)
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Error getting user: {e}")
        return None
    finally:
        SessionLocal.remove()  # Important for scoped_session


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Get user by their database ID.
    
    Args:
        user_id: User's database ID
    
    Returns:
        User object or None if not found
    """
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        logger.error(f"❌ Error getting user by ID: {e}")
        return None
    finally:
        db.close()


def update_user_profile(
    user_id: int,
    name: str = None,
    profession: str = None,
    work_schedule: str = None,
    timezone: str = None,
    motivation_style: str = None,
    goals: List[str] = None,
    preferences: Dict = None
) -> bool:
    """
    Update user profile information.
    
    Only updates fields that are provided (not None).
    
    Args:
        user_id: User's database ID
        name: User's name
        profession: What they do
        work_schedule: Their schedule
        timezone: Their timezone
        motivation_style: How they like to be motivated
        goals: List of their goals
        preferences: Dict of preferences
    
    Returns:
        True if successful, False otherwise
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Update only provided fields
        if name is not None:
            user.name = name
        if profession is not None:
            user.profession = profession
        if work_schedule is not None:
            user.work_schedule = work_schedule
        if timezone is not None:
            user.timezone = timezone
        if motivation_style is not None:
            # Convert string to enum
            user.motivation_style = MotivationStyle[motivation_style.upper()]
        if goals is not None:
            user.goals = goals
        if preferences is not None:
            user.preferences = preferences
        
        db.commit()
        logger.info(f"✅ Updated profile for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating user profile: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def complete_onboarding(user_id: int) -> bool:
    """
    Mark user's onboarding as complete.
    
    Args:
        user_id: User's database ID
    
    Returns:
        True if successful
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.onboarding_completed = True
            user.onboarding_step = 0
            db.commit()
            logger.info(f"✅ Onboarding completed for user {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error completing onboarding: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# ============================================
# TASK OPERATIONS
# ============================================

def create_task(
    user_id: int,
    task_name: str,
    description: str = None,
    due_date: datetime = None,
    priority: str = "normal",
    category: str = None,
    parent_task_id: int = None,
    estimated_time: int = None
) -> Optional[Task]:
    """
    Create a new task for a user.
    
    Args:
        user_id: User's database ID
        task_name: Name/description of the task
        description: Longer description (optional)
        due_date: When it's due (optional)
        priority: low, normal, high, urgent (default: normal)
        category: Category for organization
        parent_task_id: If this is a subtask, parent's ID
        estimated_time: Estimated minutes to complete
    
    Returns:
        Created Task object or None if failed
    """
    db = SessionLocal()
    try:
        task = Task(
            user_id=user_id,
            task_name=task_name,
            description=description,
            due_date=due_date,
            priority=TaskPriority[priority.upper()],
            category=category,
            parent_task_id=parent_task_id,
            estimated_time=estimated_time,
            status=TaskStatus.PENDING
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"✅ Created task '{task_name}' for user {user_id}")
        return task
        
    except Exception as e:
        logger.error(f"❌ Error creating task: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_user_tasks(
    user_id: int,
    status: str = None,
    limit: int = None
) -> List[Task]:
    """
    Get tasks for a user.
    
    Args:
        user_id: User's database ID
        status: Filter by status (pending, completed, etc.)
        limit: Maximum number of tasks to return
    
    Returns:
        List of Task objects
    """
    db = SessionLocal()
    try:
        query = db.query(Task).filter(Task.user_id == user_id)
        
        if status:
            query = query.filter(Task.status == TaskStatus[status.upper()])
        
        # Order by priority (urgent first) then due date
        query = query.order_by(
            Task.priority.desc(),
            Task.due_date.asc().nullslast()
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
        
    except Exception as e:
        logger.error(f"❌ Error getting tasks: {e}")
        return []
    finally:
        db.close()


def get_pending_tasks(user_id: int) -> List[Task]:
    """
    Get all pending tasks for a user.
    
    Args:
        user_id: User's database ID
    
    Returns:
        List of pending Task objects
    """
    return get_user_tasks(user_id, status="pending")


def mark_task_complete(task_id: int) -> bool:
    """
    Mark a task as completed.
    
    Also creates a Completion record for statistics.
    
    Args:
        task_id: Task's database ID
    
    Returns:
        True if successful
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        # Update task status
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        
        # Create completion record for stats
        completion = Completion(
            user_id=task.user_id,
            task_id=task.id,
            task_name=task.task_name,
            category=task.category,
            priority=task.priority.value,
            completed_at=datetime.utcnow(),
            was_on_time=task.due_date is None or datetime.utcnow() <= task.due_date
        )
        
        db.add(completion)
        db.commit()
        
        logger.info(f"✅ Task {task_id} marked complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error completing task: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def update_task_status(task_id: int, status: str) -> bool:
    """
    Update a task's status.
    
    Args:
        task_id: Task's database ID
        status: New status (pending, in_progress, completed, skipped, cancelled)
    
    Returns:
        True if successful
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        task.status = TaskStatus[status.upper()]
        
        if status == "completed":
            task.completed_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"✅ Task {task_id} status updated to {status}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating task status: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# ============================================
# CONVERSATION OPERATIONS
# ============================================

def save_conversation(
    user_id: int,
    user_message: str,
    ai_response: str,
    intent: str = None,
    context: Dict = None
) -> Optional[Conversation]:
    """
    Save a conversation exchange.
    
    Automatically maintains conversation history limit.
    
    Args:
        user_id: User's database ID
        user_message: What the user said
        ai_response: What the AI responded
        intent: Detected intent (add_task, complete_task, etc.)
        context: Additional context data
    
    Returns:
        Created Conversation object or None
    """
    db = SessionLocal()
    try:
        # Create new conversation entry
        conversation = Conversation(
            user_id=user_id,
            user_message=user_message,
            ai_response=ai_response,
            intent=intent,
            context=context or {}
        )
        
        db.add(conversation)
        
        # Clean up old conversations (keep only last MAX_CONVERSATION_MEMORY)
        old_conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(desc(Conversation.timestamp)).offset(MAX_CONVERSATION_MEMORY).all()
        
        for old_conv in old_conversations:
            db.delete(old_conv)
        
        db.commit()
        db.refresh(conversation)
        
        return conversation
        
    except Exception as e:
        logger.error(f"❌ Error saving conversation: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_conversation_history(user_id: int, limit: int = None) -> List[Conversation]:
    """
    Get recent conversation history for a user.
    
    Used for providing context to AI.
    
    Args:
        user_id: User's database ID
        limit: Max conversations to return (default: MAX_CONVERSATION_MEMORY)
    
    Returns:
        List of Conversation objects (newest first)
    """
    db = SessionLocal()
    try:
        query = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(desc(Conversation.timestamp))
        
        if limit:
            query = query.limit(limit)
        else:
            query = query.limit(MAX_CONVERSATION_MEMORY)
        
        return query.all()
        
    except Exception as e:
        logger.error(f"❌ Error getting conversation history: {e}")
        return []
    finally:
        db.close()


# ============================================
# REMINDER OPERATIONS
# ============================================

def create_reminder(
    user_id: int,
    reminder_time: datetime,
    reminder_message: str,
    priority: str = "normal",
    task_id: int = None
) -> Optional[Reminder]:
    """
    Create a new reminder.
    
    Args:
        user_id: User's database ID
        reminder_time: When to send the reminder
        reminder_message: What to remind about
        priority: optional, normal, important, critical
        task_id: Associated task ID (optional)
    
    Returns:
        Created Reminder object or None
    """
    db = SessionLocal()
    try:
        reminder = Reminder(
            user_id=user_id,
            task_id=task_id,
            reminder_time=reminder_time,
            reminder_message=reminder_message,
            priority=ReminderPriority[priority.upper()],
            status=ReminderStatus.PENDING
        )
        
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        
        logger.info(f"✅ Reminder created for user {user_id} at {reminder_time}")
        return reminder
        
    except Exception as e:
        logger.error(f"❌ Error creating reminder: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_pending_reminders() -> List[Reminder]:
    """
    Get all pending reminders that are due now.
    
    Used by the scheduler to send reminders.
    
    Returns:
        List of due Reminder objects
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        reminders = db.query(Reminder).filter(
            and_(
                Reminder.status == ReminderStatus.PENDING,
                Reminder.reminder_time <= now
            )
        ).all()
        
        return reminders
        
    except Exception as e:
        logger.error(f"❌ Error getting pending reminders: {e}")
        return []
    finally:
        db.close()


def update_reminder_status(
    reminder_id: int,
    status: str,
    nag_count: int = None
) -> bool:
    """
    Update a reminder's status.
    
    Args:
        reminder_id: Reminder's database ID
        status: New status (sent, snoozed, completed, cancelled)
        nag_count: Updated nag count (optional)
    
    Returns:
        True if successful
    """
    db = SessionLocal()
    try:
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return False
        
        reminder.status = ReminderStatus[status.upper()]
        
        if nag_count is not None:
            reminder.nag_count = nag_count
        
        if status == "completed":
            reminder.completed_at = datetime.utcnow()
        
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating reminder: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# ============================================
# IDEA OPERATIONS
# ============================================

def create_idea(
    user_id: int,
    idea_text: str,
    category: str = "General",
    notes: str = None
) -> Optional[Idea]:
    """
    Save a new idea (OTR - Off The Record).
    
    Args:
        user_id: User's database ID
        idea_text: The idea itself
        category: Category (auto-detected by AI usually)
        notes: Additional notes
    
    Returns:
        Created Idea object or None
    """
    db = SessionLocal()
    try:
        idea = Idea(
            user_id=user_id,
            idea_text=idea_text,
            category=category,
            notes=notes
        )
        
        db.add(idea)
        db.commit()
        db.refresh(idea)
        
        logger.info(f"✅ Idea saved for user {user_id}")
        return idea
        
    except Exception as e:
        logger.error(f"❌ Error creating idea: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_user_ideas(user_id: int, archived: bool = False) -> List[Idea]:
    """
    Get all ideas for a user.
    
    Args:
        user_id: User's database ID
        archived: Include archived ideas? (default: False)
    
    Returns:
        List of Idea objects
    """
    db = SessionLocal()
    try:
        query = db.query(Idea).filter(Idea.user_id == user_id)
        
        if not archived:
            query = query.filter(Idea.archived == False)
        
        return query.order_by(desc(Idea.created_at)).all()
        
    except Exception as e:
        logger.error(f"❌ Error getting ideas: {e}")
        return []
    finally:
        db.close()


# ============================================
# STATISTICS OPERATIONS
# ============================================

def get_completion_stats(user_id: int, days: int = 30) -> Dict:
    """
    Get completion statistics for a user.
    
    Args:
        user_id: User's database ID
        days: Number of days to look back (default: 30)
    
    Returns:
        Dict with stats (completed_count, completion_rate, etc.)
    """
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get completions in period
        completions = db.query(Completion).filter(
            and_(
                Completion.user_id == user_id,
                Completion.completed_at >= since
            )
        ).all()
        
        # Get tasks created in period (for completion rate)
        tasks_created = db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.created_at >= since
            )
        ).count()
        
        # Calculate stats
        completed_count = len(completions)
        on_time_count = sum(1 for c in completions if c.was_on_time)
        
        completion_rate = 0
        if tasks_created > 0:
            completion_rate = int((completed_count / tasks_created) * 100)
        
        on_time_rate = 0
        if completed_count > 0:
            on_time_rate = int((on_time_count / completed_count) * 100)
        
        return {
            'completed_count': completed_count,
            'tasks_created': tasks_created,
            'completion_rate': completion_rate,
            'on_time_count': on_time_count,
            'on_time_rate': on_time_rate,
            'period_days': days
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return {
            'completed_count': 0,
            'tasks_created': 0,
            'completion_rate': 0,
            'on_time_count': 0,
            'on_time_rate': 0,
            'period_days': days
        }
    finally:
        db.close()


# ============================================
# ASSESSMENT OPERATIONS
# ============================================

def create_assessment(
    user_id: int,
    assessment_type: str,
    period_start: datetime,
    period_end: datetime,
    assessment_text: str,
    tasks_completed: int,
    tasks_planned: int,
    completion_rate: int,
    score: int,
    patterns: Dict = None
) -> Optional[Assessment]:
    """
    Create a new assessment record.
    
    Args:
        user_id: User's database ID
        assessment_type: daily, weekly, monthly, quarterly
        period_start: Start of assessment period
        period_end: End of assessment period
        assessment_text: The actual assessment
        tasks_completed: Number completed
        tasks_planned: Number planned
        completion_rate: Percentage (0-100)
        score: Score out of 10
        patterns: Detected patterns (dict)
    
    Returns:
        Created Assessment object or None
    """
    db = SessionLocal()
    try:
        assessment = Assessment(
            user_id=user_id,
            assessment_type=assessment_type,
            period_start=period_start,
            period_end=period_end,
            assessment_text=assessment_text,
            tasks_completed=tasks_completed,
            tasks_planned=tasks_planned,
            completion_rate=completion_rate,
            score=score,
            patterns=patterns or {}
        )
        
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        logger.info(f"✅ {assessment_type} assessment created for user {user_id}")
        return assessment
        
    except Exception as e:
        logger.error(f"❌ Error creating assessment: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_latest_assessment(user_id: int, assessment_type: str) -> Optional[Assessment]:
    """
    Get the most recent assessment of a specific type.
    
    Args:
        user_id: User's database ID
        assessment_type: daily, weekly, monthly, quarterly
    
    Returns:
        Latest Assessment object or None
    """
    db = SessionLocal()
    try:
        assessment = db.query(Assessment).filter(
            and_(
                Assessment.user_id == user_id,
                Assessment.assessment_type == assessment_type
            )
        ).order_by(desc(Assessment.created_at)).first()
        
        return assessment
        
    except Exception as e:
        logger.error(f"❌ Error getting assessment: {e}")
        return None
    finally:
        db.close()
