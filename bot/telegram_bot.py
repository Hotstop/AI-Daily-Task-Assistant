"""
Telegram Bot
============

Main Telegram bot interface.
Handles all user interactions through Telegram.

By OkayYouGotMe
"""

import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from typing import Optional

from config.settings import TELEGRAM_BOT_TOKEN
from database.operations import (
    get_user_by_telegram_id, create_user,
    create_task, mark_task_complete, get_pending_tasks,
    create_idea, get_user_ideas, get_completion_stats,
    save_conversation
)
from ai.claude_engine import claude
from features.onboarding import onboarding
from bot.messages import (
    HELP_MESSAGE, ERROR_NOT_UNDERSTOOD,
    TASK_ADDED, TASK_COMPLETED, get_message
)

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Main Telegram bot class.
    
    Handles all user interactions and routes to appropriate handlers.
    """
    
    def __init__(self):
        """Initialize the Telegram bot"""
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        logger.info("🤖 Telegram Bot initialized")
    
    
    def _setup_handlers(self):
        """Set up all command and message handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("tasks", self.cmd_tasks))
        self.application.add_handler(CommandHandler("ideas", self.cmd_ideas))
        self.application.add_handler(CommandHandler("stats", self.cmd_stats))
        
        # Message handler (must be last - catches everything else)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        logger.info("✅ Bot handlers configured")
    
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command.
        
        First contact with user - start onboarding or welcome back.
        """
        try:
            telegram_id = str(update.effective_chat.id)
            user = get_user_by_telegram_id(telegram_id)
            
            if not user:
                # New user - start onboarding
                user, welcome_msg = onboarding.start_onboarding(telegram_id)
                await update.message.reply_text(welcome_msg)
                logger.info(f"👋 New user started: {telegram_id}")
            
            elif not user.onboarding_completed:
                # User exists but didn't finish onboarding
                question = onboarding.get_current_question(user)
                if question:
                    await update.message.reply_text(
                        f"Welcome back! Let's continue your setup.\n\n{question}"
                    )
                else:
                    # Onboarding somehow incomplete, restart
                    user, welcome_msg = onboarding.start_onboarding(telegram_id)
                    await update.message.reply_text(welcome_msg)
            
            else:
                # Existing user - welcome back
                pending = len(get_pending_tasks(user.id))
                
                welcome_back = f"Welcome back, {user.name}! 👋\n\n"
                
                if pending > 0:
                    welcome_back += f"You have {pending} pending task{'s' if pending != 1 else ''}.\n\n"
                else:
                    welcome_back += "You're all caught up! No pending tasks.\n\n"
                
                welcome_back += "Type /help to see what I can do!"
                
                await update.message.reply_text(welcome_back)
                logger.info(f"👋 Returning user: {user.name} ({telegram_id})")
        
        except Exception as e:
            logger.error(f"❌ Error in /start: {e}")
            await update.message.reply_text("Oops! Something went wrong. Try again?")
    
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await update.message.reply_text(HELP_MESSAGE)
        logger.info(f"❓ Help requested by {update.effective_chat.id}")
    
    
    async def cmd_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tasks command - show pending tasks"""
        try:
            telegram_id = str(update.effective_chat.id)
            user = get_user_by_telegram_id(telegram_id)
            
            if not user:
                await update.message.reply_text("You're not set up yet! Send /start to begin.")
                return
            
            tasks = get_pending_tasks(user.id)
            
            if not tasks:
                await update.message.reply_text(
                    "No pending tasks! You're all caught up! 🎉\n\n"
                    "Want to add one? Just tell me what to do!"
                )
                return
            
            # Build task list
            message = "📋 YOUR PENDING TASKS:\n\n"
            
            for idx, task in enumerate(tasks, 1):
                message += f"{idx}. {task.task_name}\n"
                
                if task.due_date:
                    message += f"   Due: {task.due_date.strftime('%b %d, %I:%M %p')}\n"
                
                if task.priority.value != "normal":
                    message += f"   Priority: {task.priority.value}\n"
                
                message += "\n"
            
            message += f"Total: {len(tasks)} task{'s' if len(tasks) != 1 else ''}\n\n"
            message += "Reply 'task X done' when you complete one!"
            
            await update.message.reply_text(message)
            logger.info(f"📋 Showed {len(tasks)} tasks to {user.name}")
        
        except Exception as e:
            logger.error(f"❌ Error in /tasks: {e}")
            await update.message.reply_text("Couldn't fetch tasks. Try again?")
    
    
    async def cmd_ideas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ideas command - show saved ideas"""
        try:
            telegram_id = str(update.effective_chat.id)
            user = get_user_by_telegram_id(telegram_id)
            
            if not user:
                await update.message.reply_text("You're not set up yet! Send /start to begin.")
                return
            
            ideas = get_user_ideas(user.id)
            
            if not ideas:
                await update.message.reply_text(
                    "No ideas saved yet!\n\n"
                    "Start with 'OTR: your idea' or 'Idea: something cool'"
                )
                return
            
            # Build ideas list
            message = "💡 YOUR SAVED IDEAS:\n\n"
            
            for idx, idea in enumerate(ideas[:10], 1):  # Show max 10
                message += f"{idx}. {idea.idea_text}\n"
                message += f"   Category: {idea.category}\n\n"
            
            if len(ideas) > 10:
                message += f"...and {len(ideas) - 10} more\n\n"
            
            message += f"Total: {len(ideas)} idea{'s' if len(ideas) != 1 else ''}"
            
            await update.message.reply_text(message)
            logger.info(f"💡 Showed {len(ideas)} ideas to {user.name}")
        
        except Exception as e:
            logger.error(f"❌ Error in /ideas: {e}")
            await update.message.reply_text("Couldn't fetch ideas. Try again?")
    
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - show statistics"""
        try:
            telegram_id = str(update.effective_chat.id)
            user = get_user_by_telegram_id(telegram_id)
            
            if not user:
                await update.message.reply_text("You're not set up yet! Send /start to begin.")
                return
            
            # Get stats for last 30 days
            stats = get_completion_stats(user.id, days=30)
            pending = len(get_pending_tasks(user.id))
            ideas = len(get_user_ideas(user.id))
            
            message = f"📊 YOUR STATS (Last 30 Days)\n\n"
            message += f"Tasks Completed: {stats['completed_count']}\n"
            message += f"Completion Rate: {stats['completion_rate']}%\n"
            message += f"On-Time Rate: {stats['on_time_rate']}%\n\n"
            message += f"Pending Tasks: {pending}\n"
            message += f"Saved Ideas: {ideas}\n\n"
            
            # Add encouragement based on completion rate
            rate = stats['completion_rate']
            if rate >= 80:
                message += "🔥 You're CRUSHING it! Keep it up!"
            elif rate >= 60:
                message += "💪 Solid work! You're making progress!"
            elif rate >= 40:
                message += "👍 Not bad, but there's room to improve!"
            else:
                message += "⚠️ Let's step it up! You can do better!"
            
            await update.message.reply_text(message)
            logger.info(f"📊 Showed stats to {user.name}")
        
        except Exception as e:
            logger.error(f"❌ Error in /stats: {e}")
            await update.message.reply_text("Couldn't fetch stats. Try again?")
    
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle regular text messages.
        
        This is where the AI magic happens!
        """
        try:
            telegram_id = str(update.effective_chat.id)
            user_message = update.message.text
            
            logger.info(f"💬 Message from {telegram_id}: {user_message[:50]}...")
            
            # Get or create user
            user = get_user_by_telegram_id(telegram_id)
            
            if not user:
                # New user - start onboarding
                user, welcome_msg = onboarding.start_onboarding(telegram_id)
                await update.message.reply_text(welcome_msg)
                return
            
            # Check if user is in onboarding
            if not user.onboarding_completed:
                success, response, is_complete = onboarding.process_answer(user, user_message)
                await update.message.reply_text(response)
                
                if is_complete:
                    logger.info(f"✅ User {user.name} completed onboarding")
                
                return
            
            # User is set up - process with AI
            await self._process_with_ai(update, user, user_message)
        
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            await update.message.reply_text(ERROR_NOT_UNDERSTOOD)
    
    
    async def _process_with_ai(self, update: Update, user, user_message: str):
        """
        Process message with AI intelligence.
        
        Args:
            update: Telegram update
            user: User object
            user_message: What the user said
        """
        try:
            # Get context
            pending_tasks = get_pending_tasks(user.id)
            stats = get_completion_stats(user.id, days=7)
            
            context = {
                'pending_tasks': len(pending_tasks),
                'completion_rate': stats['completion_rate']
            }
            
            # Analyze intent
            intent_result = claude.analyze_intent(user_message, user)
            intent = intent_result.get('intent', 'chat')
            
            logger.info(f"🧠 Intent: {intent}")
            
            # Route based on intent
            if intent == 'add_task':
                await self._handle_add_task(update, user, intent_result)
            
            elif intent == 'complete_task':
                await self._handle_complete_task(update, user, intent_result)
            
            elif intent == 'add_idea':
                await self._handle_add_idea(update, user, intent_result)
            
            elif intent == 'view_tasks':
                await self.cmd_tasks(update, None)
            
            elif intent == 'view_ideas':
                await self.cmd_ideas(update, None)
            
            else:
                # Generate AI response
                response = claude.generate_response(user_message, user, context)
                await update.message.reply_text(response)
                
                # Save conversation
                save_conversation(user.id, user_message, response, intent)
        
        except Exception as e:
            logger.error(f"❌ Error in AI processing: {e}")
            await update.message.reply_text("Hmm, I'm having trouble understanding. Can you rephrase?")
    
    
    async def _handle_add_task(self, update: Update, user, intent_result: dict):
        """Handle adding a new task"""
        try:
            task_name = intent_result.get('task_name', update.message.text)
            
            # Check if task should be broken down
            breakdown = claude.break_down_task(task_name, user)
            
            if breakdown.get('should_break_down') and breakdown.get('subtasks'):
                # Offer to break it down
                subtasks = breakdown['subtasks']
                total_time = breakdown['total_estimated_time']
                
                message = f"That's a big task! Let me break it down:\n\n"
                for idx, subtask in enumerate(subtasks, 1):
                    message += f"{idx}. {subtask['name']} ({subtask['estimated_time']} min)\n"
                
                message += f"\nTotal: ~{total_time} minutes\n\n"
                message += "Want me to add it this way? Reply 'yes' or 'no'"
                
                await update.message.reply_text(message)
                return
            
            # Create task
            task = create_task(user.id, task_name)
            
            if task:
                # Get appropriate message based on motivation style
                motivation = user.motivation_style.value if user.motivation_style else "direct"
                total_tasks = len(get_pending_tasks(user.id))
                
                response = get_message(
                    TASK_ADDED,
                    motivation,
                    task_name=task_name,
                    total_tasks=total_tasks
                )
                
                await update.message.reply_text(response)
                logger.info(f"✅ Task added for {user.name}: {task_name}")
            else:
                await update.message.reply_text("Couldn't add that task. Try again?")
        
        except Exception as e:
            logger.error(f"❌ Error adding task: {e}")
            await update.message.reply_text("Oops! Couldn't add that task.")
    
    
    async def _handle_complete_task(self, update: Update, user, intent_result: dict):
        """Handle completing a task"""
        try:
            # Get task ID from intent
            task_id_str = intent_result.get('task_id')
            
            if task_id_str:
                # User said "task 1 done"
                try:
                    task_num = int(task_id_str)
                    tasks = get_pending_tasks(user.id)
                    
                    if 0 < task_num <= len(tasks):
                        task = tasks[task_num - 1]
                        
                        if mark_task_complete(task.id):
                            motivation = user.motivation_style.value if user.motivation_style else "direct"
                            remaining = len(get_pending_tasks(user.id))
                            
                            response = get_message(
                                TASK_COMPLETED,
                                motivation,
                                task_name=task.task_name,
                                remaining_tasks=remaining
                            )
                            
                            await update.message.reply_text(response)
                            logger.info(f"✅ Task completed: {task.task_name}")
                            return
                    
                    await update.message.reply_text(f"Task #{task_num} not found. Use /tasks to see your list.")
                
                except ValueError:
                    await update.message.reply_text("Which task? Try 'task 1 done' or 'task 2 done'")
            
            else:
                await update.message.reply_text("Which task did you complete? Reply 'task 1 done' or similar.")
        
        except Exception as e:
            logger.error(f"❌ Error completing task: {e}")
            await update.message.reply_text("Couldn't mark that complete. Try again?")
    
    
    async def _handle_add_idea(self, update: Update, user, intent_result: dict):
        """Handle saving an idea (OTR)"""
        try:
            idea_text = intent_result.get('idea', update.message.text)
            
            # Remove OTR prefix if present
            for prefix in ['OTR:', 'Idea:', 'Remember:', 'Save this:']:
                if idea_text.startswith(prefix):
                    idea_text = idea_text[len(prefix):].strip()
                    break
            
            # Auto-categorize
            category = claude.categorize_idea(idea_text, user)
            
            # Save idea
            idea = create_idea(user.id, idea_text, category)
            
            if idea:
                response = f"💡 Idea Saved!\n\n{idea_text}\n\nCategory: {category}"
                await update.message.reply_text(response)
                logger.info(f"💡 Idea saved for {user.name}: {idea_text[:50]}...")
            else:
                await update.message.reply_text("Couldn't save that idea. Try again?")
        
        except Exception as e:
            logger.error(f"❌ Error saving idea: {e}")
            await update.message.reply_text("Oops! Couldn't save that idea.")
    
    
    async def send_message(self, chat_id: str, message: str):
        """
        Send a message to a user.
        
        Used by reminders and assessments.
        
        Args:
            chat_id: Telegram chat ID
            message: Message to send
        """
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            logger.info(f"📤 Message sent to {chat_id}")
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
    
    
    async def start(self):
        """Start the bot (async)"""
        logger.info("🚀 Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
    
    
    def run(self):
        """Run the bot (blocking)"""
        logger.info("🚀 Starting Telegram bot in blocking mode...")
        self.application.run_polling()


# Import asyncio at the end to avoid circular imports
import asyncio
