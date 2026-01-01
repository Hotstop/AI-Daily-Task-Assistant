"""
Configuration Settings
======================

ALL settings in one place - easy to understand and modify!

Change these values to customize how the AI assistant behaves.
No need to dig through code - everything is here.

By OkayYouGotMe
"""

import os
from typing import Dict, List

# ============================================
# CORE CREDENTIALS
# ============================================
# These come from environment variables (set in Railway or .env file)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Optional: Weather API (get free key from openweathermap.org)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")


# ============================================
# AI BEHAVIOR SETTINGS
# ============================================

# Claude Model to Use
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Latest Sonnet model

# AI Creativity Level (0.0 = robotic, 1.0 = very creative)
# 0.7 is a good balance for task management
AI_TEMPERATURE = 0.7

# How many previous messages to remember in conversation
# Higher = more context, but slower responses
MAX_CONVERSATION_MEMORY = 10

# Brutal Honesty Level in Assessments
# Options: "low" (gentle), "medium" (balanced), "high" (brutally honest)
BRUTAL_HONESTY_LEVEL = "high"

# Include emojis in assessments and messages?
USE_EMOJIS = True


# ============================================
# TIMING SETTINGS
# ============================================

# Default timezone for all users (can be overridden per user)
DEFAULT_TIMEZONE = "America/New_York"

# Hourly Check-in Times (24-hour format)
HOURLY_CHECKIN_START = 9   # Start at 9 AM
HOURLY_CHECKIN_END = 23    # End at 11 PM

# Daily Assessment Time (24-hour format HH:MM)
DAILY_ASSESSMENT_TIME = "22:00"  # 10 PM

# Weekly Assessment (day of week)
WEEKLY_ASSESSMENT_DAY = "sunday"  # Options: monday, tuesday, etc.
WEEKLY_ASSESSMENT_TIME = "22:00"

# Monthly Assessment (day of month)
MONTHLY_ASSESSMENT_DAY = "last"  # Last day of month
MONTHLY_ASSESSMENT_TIME = "22:00"


# ============================================
# REMINDER SETTINGS
# ============================================

# How often to nag for each priority level (in minutes)
# Example: [0, 5, 10] means: remind immediately, then after 5 min, then after 10 min

REMINDER_INTERVALS: Dict[str, List[int]] = {
    # Critical: Nag every 5 minutes until confirmed
    'critical': [0, 5, 10, 15, 20],
    
    # Important: Nag 3 times total
    'important': [0, 15, 30],
    
    # Normal: Remind twice
    'normal': [0, 30],
    
    # Optional: Remind once only
    'optional': [0]
}

# Maximum number of reminders before giving up
MAX_REMINDER_ATTEMPTS = 5


# ============================================
# TASK MANAGEMENT SETTINGS
# ============================================

# Auto-break down tasks longer than this many minutes
AUTO_BREAKDOWN_THRESHOLD = 60  # 1 hour

# Maximum number of subtasks to create
MAX_SUBTASKS = 5

# Default task statuses available
TASK_STATUSES = ['pending', 'in_progress', 'completed', 'skipped', 'cancelled']

# Task priority levels
TASK_PRIORITIES = ['low', 'normal', 'high', 'urgent']


# ============================================
# ASSESSMENT SETTINGS
# ============================================

# Score tasks out of this number
SCORE_OUT_OF = 10

# Minimum completion rate to be considered "good"
GOOD_COMPLETION_RATE = 75  # 75%

# Completion rate thresholds for different ratings
COMPLETION_THRESHOLDS = {
    'excellent': 90,  # 90%+
    'good': 75,       # 75-89%
    'average': 60,    # 60-74%
    'below_average': 45,  # 45-59%
    'poor': 0         # Below 45%
}


# ============================================
# ONBOARDING SETTINGS
# ============================================

# Questions to ask during onboarding (in order)
ONBOARDING_QUESTIONS = [
    {
        'id': 'name',
        'question': "What's your name?",
        'type': 'text'
    },
    {
        'id': 'profession',
        'question': "What do you do? (work/study/both)",
        'type': 'text'
    },
    {
        'id': 'challenge',
        'question': """What's your biggest productivity challenge?
a) Staying focused
b) Remembering everything
c) Prioritizing tasks
d) Work-life balance

Reply with the letter (a, b, c, or d)""",
        'type': 'choice',
        'options': ['a', 'b', 'c', 'd']
    },
    {
        'id': 'motivation_style',
        'question': """How do you like to be motivated?
a) Gentle nudges
b) Direct & honest (brutally honest)
c) Celebrate wins
d) Just the facts

Reply with the letter (a, b, c, or d)""",
        'type': 'choice',
        'options': ['a', 'b', 'c', 'd']
    },
    {
        'id': 'goals',
        'question': "What are your main goals right now? (You can list multiple)",
        'type': 'text'
    },
    {
        'id': 'schedule',
        'question': "What's your typical work/study schedule? (e.g., '9-5 weekdays', '12-hour shifts', etc.)",
        'type': 'text'
    }
]

# Motivation style mapping
MOTIVATION_STYLES = {
    'a': 'gentle',      # Gentle nudges
    'b': 'direct',      # Brutally honest
    'c': 'celebrate',   # Celebrate wins
    'd': 'factual'      # Just the facts
}

# Challenge mapping
CHALLENGES = {
    'a': 'focus',           # Staying focused
    'b': 'memory',          # Remembering everything
    'c': 'prioritization',  # Prioritizing tasks
    'd': 'balance'          # Work-life balance
}


# ============================================
# FEATURE TOGGLES
# ============================================

# Enable/disable specific features easily

# External integrations
ENABLE_WEATHER = True           # Allow weather requests
ENABLE_WEB_SEARCH = True        # Allow web searches
ENABLE_NEWS = True              # Allow news requests

# AI features
ENABLE_TASK_BREAKDOWN = True    # Auto-break down big tasks
ENABLE_PATTERN_DETECTION = True # Detect user behavior patterns
ENABLE_SMART_REDIRECT = True    # Redirect off-topic questions

# Assessment features
ENABLE_DAILY_ASSESSMENT = True
ENABLE_WEEKLY_ASSESSMENT = True
ENABLE_MONTHLY_ASSESSMENT = True
ENABLE_QUARTERLY_ASSESSMENT = True

# Reminder features
ENABLE_PERSISTENT_REMINDERS = True
ENABLE_SNOOZE = True            # Allow users to snooze reminders


# ============================================
# MESSAGE CUSTOMIZATION
# ============================================

# Brand name (appears in messages)
BRAND_NAME = "AI Task Assistant"
BRAND_TAGLINE = "By OkayYouGotMe"

# Welcome message for new users
WELCOME_MESSAGE = f"""Hey! Welcome to {BRAND_NAME}!

I'm your AI productivity partner. I'll help you:
• Stay on top of your tasks
• Break down overwhelming projects
• Give you brutally honest feedback
• Keep you accountable to your goals

Let's get you set up! Takes just 2 minutes.

Ready? Reply 'yes' to start!"""


# ============================================
# LOGGING SETTINGS
# ============================================

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Save logs to file?
SAVE_LOGS_TO_FILE = True
LOG_FILE_PATH = "ai_assistant.log"


# ============================================
# PERFORMANCE SETTINGS
# ============================================

# Database connection pool size
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# API timeout (seconds)
API_TIMEOUT = 30

# Rate limiting (requests per minute per user)
MAX_REQUESTS_PER_MINUTE = 30


# ============================================
# VALIDATION
# ============================================

def validate_config():
    """
    Check if all required settings are properly configured.
    Raises error if something is missing or invalid.
    """
    errors = []
    
    # Check required credentials
    if not TELEGRAM_BOT_TOKEN:
        errors.append("❌ TELEGRAM_BOT_TOKEN is missing")
    
    if not CLAUDE_API_KEY:
        errors.append("❌ CLAUDE_API_KEY is missing")
    
    if not DATABASE_URL:
        errors.append("❌ DATABASE_URL is missing")
    
    # Check value ranges
    if not (0 <= AI_TEMPERATURE <= 1):
        errors.append("❌ AI_TEMPERATURE must be between 0 and 1")
    
    if MAX_CONVERSATION_MEMORY < 1:
        errors.append("❌ MAX_CONVERSATION_MEMORY must be at least 1")
    
    if BRUTAL_HONESTY_LEVEL not in ['low', 'medium', 'high']:
        errors.append("❌ BRUTAL_HONESTY_LEVEL must be 'low', 'medium', or 'high'")
    
    # If there are errors, print them and raise exception
    if errors:
        print("\n⚠️  CONFIGURATION ERRORS:\n")
        for error in errors:
            print(f"   {error}")
        print("\n   Fix these in your .env file or Railway environment variables!\n")
        raise ValueError("Configuration validation failed")
    
    print("✅ Configuration validated successfully!")


# Run validation when this file is imported
if __name__ != "__main__":
    validate_config()
