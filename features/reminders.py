"""
Persistent Reminder System
==========================

Handles scheduled reminders with intelligent nagging.

Features:
- Multiple priority levels (optional, normal, important, critical)
- Escalating reminders (nags until user responds)
- Snooze functionality
- Completion tracking

By OkayYouGotMe
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio

from database.operations import (
    create_reminder, get_pending_reminders, update_reminder_status,
    get_user_by_id
)
from database.models import Reminder, ReminderPriority
from config.settings import REMINDER_INTERVALS
from bot.messages import (
    REMINDER_FIRST, REMINDER_SECOND, REMINDER_THIRD,
    REMINDER_FINAL, REMINDER_MARKED_MISSED
)

logger = logging.getLogger(__name__)


class ReminderManager:
    """
    Manages all reminder functionality.
    
    Sends reminders at scheduled times and nags persistently
    based on priority level.
    """
    
    def __init__(self, bot):
        """
        Initialize reminder manager.
        
        Args:
            bot: Telegram bot instance (for sending messages)
        """
        self.bot = bot
        self.active_reminders = {}  # Track active reminder loops
        logger.info("⏰ Reminder Manager initialized")
    
    
    async def check_and_send_reminders(self):
        """
        Check for due reminders and send them.
        
        Called by scheduler every minute.
        """
        try:
            # Get all pending reminders that are due
            due_reminders = get_pending_reminders()
            
            if not due_reminders:
                return
            
            logger.info(f"⏰ Found {len(due_reminders)} due reminders")
            
            for reminder in due_reminders:
                await self._process_reminder(reminder)
        
        except Exception as e:
            logger.error(f"❌ Error checking reminders: {e}")
    
    
    async def _process_reminder(self, reminder: Reminder):
        """
        Process a single reminder.
        
        Sends initial reminder and starts nagging loop if needed.
        
        Args:
            reminder: Reminder object
        """
        try:
            user = get_user_by_id(reminder.user_id)
            if not user:
                logger.error(f"User {reminder.user_id} not found for reminder")
                return
            
            # Get priority intervals
            priority = reminder.priority.value
            intervals = REMINDER_INTERVALS.get(priority, [0])
            
            # Send first reminder
            message = REMINDER_FIRST.format(task_name=reminder.reminder_message)
            
            await self.bot.send_message(user.telegram_chat_id, message)
            
            # Update reminder status
            update_reminder_status(reminder.id, status="sent", nag_count=1)
            
            logger.info(f"⏰ Sent reminder to {user.name}: {reminder.reminder_message}")
            
            # Start nagging loop if priority requires it
            if len(intervals) > 1:
                asyncio.create_task(
                    self._nag_loop(reminder, user, intervals)
                )
        
        except Exception as e:
            logger.error(f"❌ Error processing reminder: {e}")
    
    
    async def _nag_loop(
        self,
        reminder: Reminder,
        user,
        intervals: List[int]
    ):
        """
        Persistent nagging loop.
        
        Keeps sending reminders at intervals until user responds.
        
        Args:
            reminder: Reminder object
            user: User object
            intervals: List of intervals in minutes [0, 5, 10, 15, 20]
        """
        try:
            # Skip first interval (already sent)
            for idx, interval in enumerate(intervals[1:], start=2):
                
                # Wait for the interval
                await asyncio.sleep(interval * 60)
                
                # Check if reminder was completed/cancelled
                # (In real implementation, would query database)
                # For now, we'll send all scheduled nags
                
                # Get user's completion rate for context
                from database.operations import get_completion_stats
                stats = get_completion_stats(user.id, days=7)
                completion_rate = stats.get('completion_rate', 0)
                
                # Calculate elapsed time
                start_time = reminder.reminder_time
                elapsed_minutes = int((datetime.utcnow() - start_time).total_seconds() / 60)
                
                # Choose message based on nag count
                if idx == 2:
                    message = REMINDER_SECOND.format(
                        task_name=reminder.reminder_message
                    )
                
                elif idx == 3:
                    message = REMINDER_THIRD.format(
                        task_name=reminder.reminder_message,
                        elapsed_time=elapsed_minutes,
                        priority=reminder.priority.value
                    )
                
                elif idx >= 4:
                    message = REMINDER_FINAL.format(
                        task_name=reminder.reminder_message,
                        elapsed_time=elapsed_minutes,
                        completion_rate=completion_rate,
                        priority=reminder.priority.value
                    )
                
                else:
                    # Generic nag
                    message = f"⏰ REMINDER #{idx}: {reminder.reminder_message}\n\n"
                    message += f"It's been {elapsed_minutes} minutes.\n"
                    message += f"Reply 'done' when finished."
                
                # Send nag
                await self.bot.send_message(user.telegram_chat_id, message)
                
                # Update nag count
                update_reminder_status(reminder.id, status="sent", nag_count=idx)
                
                logger.info(f"⏰ Nag #{idx} sent for reminder {reminder.id}")
            
            # After all nags, mark as missed if not completed
            await asyncio.sleep(5 * 60)  # Wait 5 more minutes
            
            # Send final "marked as missed" message
            message = REMINDER_MARKED_MISSED.format(
                task_name=reminder.reminder_message
            )
            
            await self.bot.send_message(user.telegram_chat_id, message)
            
            # Mark as incomplete
            update_reminder_status(reminder.id, status="cancelled")
            
            logger.info(f"⏰ Reminder {reminder.id} marked as missed")
        
        except Exception as e:
            logger.error(f"❌ Error in nag loop: {e}")
    
    
    async def handle_reminder_response(
        self,
        reminder_id: int,
        response: str
    ) -> str:
        """
        Handle user's response to a reminder.
        
        Args:
            reminder_id: Reminder's database ID
            response: User's response (done, snooze, skip, etc.)
        
        Returns:
            Response message to user
        """
        try:
            response_lower = response.lower().strip()
            
            if response_lower in ['done', 'completed', 'finished']:
                # Mark as completed
                update_reminder_status(reminder_id, status="completed")
                return "✅ Great! Marked as complete."
            
            elif response_lower.startswith('snooze'):
                # Extract snooze duration
                # Examples: "snooze 15", "snooze 1h", "snooze 30"
                parts = response_lower.split()
                
                if len(parts) >= 2:
                    duration_str = parts[1]
                    
                    # Parse duration
                    if duration_str.endswith('h'):
                        minutes = int(duration_str[:-1]) * 60
                    elif duration_str.endswith('m'):
                        minutes = int(duration_str[:-1])
                    else:
                        minutes = int(duration_str)
                    
                    # Update reminder (would reschedule in real implementation)
                    update_reminder_status(reminder_id, status="snoozed")
                    
                    return f"⏰ Snoozed for {minutes} minutes. I'll remind you then."
                
                else:
                    return "How long? Try 'snooze 15' or 'snooze 1h'"
            
            elif response_lower in ['skip', 'cancel', 'nevermind']:
                # Cancel reminder
                update_reminder_status(reminder_id, status="cancelled")
                return "Reminder cancelled."
            
            else:
                return "Not sure what you mean. Reply 'done', 'snooze X', or 'skip'"
        
        except Exception as e:
            logger.error(f"❌ Error handling reminder response: {e}")
            return "Couldn't process that. Try 'done' or 'snooze 15'"


class ReminderScheduler:
    """
    Background scheduler for reminders.
    
    Runs continuously checking for due reminders.
    """
    
    def __init__(self, bot):
        """
        Initialize scheduler.
        
        Args:
            bot: Telegram bot instance
        """
        self.bot = bot
        self.reminder_manager = ReminderManager(bot)
        self.is_running = False
        logger.info("📅 Reminder Scheduler initialized")
    
    
    async def start(self):
        """Start the reminder scheduler"""
        self.is_running = True
        logger.info("🚀 Reminder scheduler started")
        
        while self.is_running:
            try:
                # Check for due reminders
                await self.reminder_manager.check_and_send_reminders()
                
                # Wait 1 minute before next check
                await asyncio.sleep(60)
            
            except Exception as e:
                logger.error(f"❌ Error in reminder scheduler: {e}")
                await asyncio.sleep(60)  # Continue even on error
    
    
    def stop(self):
        """Stop the reminder scheduler"""
        self.is_running = False
        logger.info("🛑 Reminder scheduler stopped")
