"""
Onboarding System
=================

Guides new users through setup questionnaire.

Collects information to personalize the AI assistant.
Makes it feel natural and conversational.

By OkayYouGotMe
"""

import logging
from typing import Optional, Dict
from datetime import datetime

from database.models import User
from database.operations import (
    create_user, update_user_profile, complete_onboarding, get_user_by_id
)
from config.settings import (
    ONBOARDING_QUESTIONS, MOTIVATION_STYLES, CHALLENGES
)
from bot.messages import (
    WELCOME_NEW_USER, ONBOARDING_INTRO, ONBOARDING_COMPLETE
)

logger = logging.getLogger(__name__)


class OnboardingManager:
    """
    Manages the onboarding flow for new users.
    
    Asks 6 questions to build user profile:
    1. Name
    2. Profession
    3. Biggest challenge
    4. Motivation style
    5. Goals
    6. Schedule
    """
    
    def __init__(self):
        """Initialize onboarding manager"""
        self.questions = ONBOARDING_QUESTIONS
        logger.info("📋 Onboarding Manager initialized")
    
    
    def start_onboarding(self, telegram_chat_id: str) -> tuple[User, str]:
        """
        Start onboarding for a new user.
        
        Args:
            telegram_chat_id: User's Telegram chat ID
        
        Returns:
            (User object, welcome message)
        """
        try:
            # Create new user
            user = create_user(telegram_chat_id)
            
            if not user:
                return None, "Sorry, couldn't create your profile. Try again?"
            
            logger.info(f"✅ Starting onboarding for user {user.id}")
            
            # Return welcome message
            return user, WELCOME_NEW_USER
            
        except Exception as e:
            logger.error(f"❌ Error starting onboarding: {e}")
            return None, "Oops, something went wrong. Can you try again?"
    
    
    def get_current_question(self, user: User) -> Optional[str]:
        """
        Get the current onboarding question for a user.
        
        Args:
            user: User object
        
        Returns:
            Question text or None if onboarding complete
        """
        try:
            if user.onboarding_completed:
                return None
            
            step = user.onboarding_step
            
            # Check if we've asked all questions
            if step >= len(self.questions):
                return None
            
            question_data = self.questions[step]
            return question_data['question']
            
        except Exception as e:
            logger.error(f"❌ Error getting question: {e}")
            return None
    
    
    def process_answer(
        self,
        user: User,
        answer: str
    ) -> tuple[bool, str, bool]:
        """
        Process user's answer to current onboarding question.
        
        Args:
            user: User object
            answer: User's answer
        
        Returns:
            (success, response_message, is_complete)
        """
        try:
            step = user.onboarding_step
            
            if step >= len(self.questions):
                return False, "Onboarding already complete!", True
            
            question_data = self.questions[step]
            question_id = question_data['id']
            
            # Validate answer if it's a choice question
            if question_data['type'] == 'choice':
                answer = answer.lower().strip()
                if answer not in question_data.get('options', []):
                    valid_options = ", ".join(question_data['options'])
                    return False, f"Please choose one of: {valid_options}", False
            
            # Store the answer
            success = self._store_answer(user, question_id, answer)
            
            if not success:
                return False, "Couldn't save that answer. Try again?", False
            
            # Move to next question
            user.onboarding_step = step + 1
            
            # Check if onboarding is complete
            if user.onboarding_step >= len(self.questions):
                complete_onboarding(user.id)
                return True, ONBOARDING_COMPLETE, True
            
            # Get next question
            next_question = self.get_current_question(user)
            
            # Create encouraging transition
            response = self._get_acknowledgment(question_id, answer)
            response += f"\n\n{next_question}"
            
            logger.info(f"✅ User {user.id} answered question {step}")
            
            return True, response, False
            
        except Exception as e:
            logger.error(f"❌ Error processing answer: {e}")
            return False, "Oops, something went wrong. Can you try that again?", False
    
    
    def _store_answer(self, user: User, question_id: str, answer: str) -> bool:
        """
        Store user's answer to onboarding question.
        
        Args:
            user: User object
            question_id: Which question (name, profession, etc.)
            answer: User's answer
        
        Returns:
            True if successful
        """
        try:
            # Prepare update data
            update_data = {}
            
            if question_id == 'name':
                update_data['name'] = answer.strip()
            
            elif question_id == 'profession':
                update_data['profession'] = answer.strip()
            
            elif question_id == 'challenge':
                # Map letter to challenge
                challenge = CHALLENGES.get(answer.lower(), 'unknown')
                # Store in preferences
                prefs = user.preferences or {}
                prefs['main_challenge'] = challenge
                update_data['preferences'] = prefs
            
            elif question_id == 'motivation_style':
                # Map letter to style
                style = MOTIVATION_STYLES.get(answer.lower(), 'direct')
                update_data['motivation_style'] = style
            
            elif question_id == 'goals':
                # Parse goals (split by comma or newline)
                goals_list = []
                for goal in answer.replace('\n', ',').split(','):
                    goal = goal.strip()
                    if goal:
                        goals_list.append(goal)
                update_data['goals'] = goals_list
            
            elif question_id == 'schedule':
                update_data['work_schedule'] = answer.strip()
            
            # Update user profile
            return update_user_profile(user.id, **update_data)
            
        except Exception as e:
            logger.error(f"❌ Error storing answer: {e}")
            return False
    
    
    def _get_acknowledgment(self, question_id: str, answer: str) -> str:
        """
        Get a personalized acknowledgment for the answer.
        
        Makes the flow feel more conversational.
        
        Args:
            question_id: Which question was answered
            answer: User's answer
        
        Returns:
            Acknowledgment message
        """
        acknowledgments = {
            'name': f"Nice to meet you, {answer.split()[0]}! 👋",
            
            'profession': {
                'nurse': "Healthcare hero! 🏥 Respect.",
                'doctor': "Healthcare hero! 🏥 Respect.",
                'teacher': "Shaping minds! 📚 Love it.",
                'engineer': "Building the future! 🔧 Nice.",
                'student': "Invest in yourself now, reap rewards later! 📖",
                'default': f"{answer} - got it!"
            },
            
            'challenge': {
                'a': "Staying focused - that's what I'm here for!",
                'b': "Memory support - I've got you covered!",
                'c': "Prioritization - we'll work on that together!",
                'd': "Work-life balance - let's find it!"
            },
            
            'motivation_style': {
                'a': "Gentle nudges - I'll be patient with you.",
                'b': "Brutally honest - I won't sugarcoat things. Deal?",
                'c': "Celebrate wins - let's make every day a victory! 🎯",
                'd': "Just the facts - I'll keep it concise."
            },
            
            'goals': f"Love it! {len(answer.split(','))} solid goals to work toward.",
            
            'schedule': "Got it - I'll respect your schedule."
        }
        
        # Get acknowledgment
        ack = acknowledgments.get(question_id, "Got it!")
        
        # Handle dict-based acknowledgments (like profession)
        if isinstance(ack, dict):
            # Check for keywords in answer
            answer_lower = answer.lower()
            for keyword, message in ack.items():
                if keyword != 'default' and keyword in answer_lower:
                    return message
            return ack.get('default', "Got it!")
        
        # Handle choice-based acknowledgments
        elif isinstance(ack, str) and '{' not in ack:
            return ack
        
        else:
            # For motivation_style and challenge, answer is a letter
            return acknowledgments[question_id].get(answer.lower(), "Got it!")
    
    
    def skip_onboarding(self, user: User) -> bool:
        """
        Skip onboarding and set defaults.
        
        Args:
            user: User object
        
        Returns:
            True if successful
        """
        try:
            # Set basic defaults
            update_user_profile(
                user.id,
                name="User",
                motivation_style="direct"
            )
            
            complete_onboarding(user.id)
            
            logger.info(f"⏭️ User {user.id} skipped onboarding")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error skipping onboarding: {e}")
            return False


# Create global instance
onboarding = OnboardingManager()
