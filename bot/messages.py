"""
Bot Messages
============

ALL bot messages in one place - easy to edit the personality!

Want to change how the bot talks? Just edit these strings.
No need to dig through code.

Messages are organized by:
- Motivation style (gentle, direct, celebrate, factual)
- Context (onboarding, tasks, assessments, etc.)

By OkayYouGotMe
"""

from typing import Dict

# ============================================
# WELCOME & ONBOARDING
# ============================================

WELCOME_NEW_USER = """Hey! Welcome to AI Task Assistant! 👋

I'm your AI productivity partner. I'll help you:
• Stay on top of your tasks
• Break down overwhelming projects  
• Give you brutally honest feedback
• Keep you accountable to your goals

Let's get you set up! Takes just 2 minutes.

Ready? Reply 'yes' to start!"""


ONBOARDING_INTRO = """Great! Let's learn about you so I can help better.

I'll ask 6 quick questions. Just answer naturally - no pressure!

First question coming up..."""


ONBOARDING_COMPLETE = """✅ Profile complete! 

I know who you are, what you do, and how you like to work.

Now I can actually HELP you instead of just being another generic bot.

Try these to get started:
• "Remind me to call John at 4pm"
• "I need to prepare for Friday's presentation"
• "What are my tasks?"
• "OTR: Great idea I just had"

Let's do this! 💪"""


# ============================================
# TASK CONFIRMATION MESSAGES
# ============================================

# Different styles based on user's motivation preference

TASK_ADDED: Dict[str, str] = {
    'gentle': "✅ I've added '{task_name}' for you. Take your time with it when you're ready.",
    
    'direct': "✅ Done. '{task_name}' is on your list. Handle it.",
    
    'celebrate': "🎯 Yes! Added '{task_name}' to your list. You've got {total_tasks} opportunities to win today!",
    
    'factual': "✅ Task added: '{task_name}'. Status: Pending."
}


TASK_COMPLETED: Dict[str, str] = {
    'gentle': "✅ Nice work on '{task_name}'! One step at a time, you're making progress.",
    
    'direct': "✅ '{task_name}' done. {remaining_tasks} left. Keep moving.",
    
    'celebrate': "🎉 YES! '{task_name}' crushed! You're on fire! {remaining_tasks} to go!",
    
    'factual': "✅ Task completed: '{task_name}'. Remaining: {remaining_tasks}."
}


TASK_SKIPPED: Dict[str, str] = {
    'gentle': "Okay, I've marked '{task_name}' as skipped. No judgment - sometimes priorities change.",
    
    'direct': "'{task_name}' skipped. Just don't make a habit of it.",
    
    'celebrate': "Alright, '{task_name}' is skipped. Focus on winning the important ones! 🎯",
    
    'factual': "Task skipped: '{task_name}'. Status updated."
}


# ============================================
# TASK BREAKDOWN MESSAGES
# ============================================

TASK_TOO_BIG = """That's a BIG task. Let me break it down so you don't get overwhelmed.

Instead of one giant task, how about these manageable steps:

{breakdown}

Total estimated time: ~{total_time} minutes

Want me to add it this way? Or keep it as one task?"""


BREAKDOWN_CONFIRMATION = """✅ Perfect! I've added {num_subtasks} steps:

{subtask_list}

Tackle them one at a time. You've got this! 💪"""


# ============================================
# REMINDER MESSAGES
# ============================================

REMINDER_SET: Dict[str, str] = {
    'gentle': "✅ I'll gently remind you about '{task_name}' at {time}.",
    
    'direct': "✅ Reminder set for {time}. I'll make sure you don't forget '{task_name}'.",
    
    'celebrate': "🎯 Got it! I'll ping you at {time} about '{task_name}'. Let's nail it!",
    
    'factual': "✅ Reminder scheduled: {time} for '{task_name}'."
}


# First reminder (friendly)
REMINDER_FIRST = """⏰ TIME: {task_name}

This is what you asked me to remind you about.

Reply 'done' when finished, or 'snooze 15' to delay."""


# Second reminder (firmer)
REMINDER_SECOND = """⏰ SECOND REMINDER: {task_name}

You haven't responded yet.
You ASKED me to remind you.

So here I am. Reminding you.

Reply 'done' or 'snooze X minutes'"""


# Third reminder (direct)
REMINDER_THIRD = """⏰ THIRD REMINDER: {task_name}

Seriously? It's been {elapsed_time} minutes.

Either:
1. Do it RIGHT NOW
2. Reply 'skip' if plans changed  
3. Reply 'snooze 30' to delay

But don't ignore me. That's disrespecting yourself."""


# Final reminder (brutally honest)
REMINDER_FINAL = """⏰ FINAL WARNING: {task_name}

{elapsed_time} minutes. No action.

This is why your completion rate is {completion_rate}%.

You set this as {priority}. Act like it.

Last chance. After this, I'm marking it as missed."""


REMINDER_MARKED_MISSED = """⏰ MARKED AS INCOMPLETE

You didn't do '{task_name}'.
You didn't respond.

I'm marking this as MISSED.

This will show up in your assessment tonight under "Commitments You Broke."

If you DID complete it, reply 'done' and I'll fix the record.

Otherwise, own this failure and do better tomorrow."""


# ============================================
# DAILY SIMPLIFICATION
# ============================================

DAILY_MORNING_SIMPLE = """Good morning{name}! ☀️

Today: {date}
Weather: {weather}

You have {total_tasks} tasks. Let me simplify:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUICK WINS (Do first - {quick_wins_time} min):
{quick_wins}

Knock these out early for momentum!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BIG FOCUS (Needs concentration):
{big_focus}
Best time: {best_time} (when you're sharpest)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLEX TASKS (Fit in whenever):
{flex_tasks}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to crush it? 💪"""


# ============================================
# ASSESSMENT MESSAGES
# ============================================

# These adapt based on brutality level and motivation style

DAILY_ASSESSMENT_INTRO: Dict[str, Dict[str, str]] = {
    'low': {  # Low brutality
        'gentle': "Let's review your day gently...",
        'direct': "Here's your daily review...",
        'celebrate': "Let's see what you accomplished today!",
        'factual': "Daily performance summary:"
    },
    'medium': {  # Medium brutality
        'gentle': "Time for an honest look at today...",
        'direct': "Daily debrief - the real story:",
        'celebrate': "Daily check-in - wins and opportunities:",
        'factual': "Daily analysis:"
    },
    'high': {  # High brutality
        'gentle': "We need to talk about today...",
        'direct': "THE TRUTH about your day:",
        'celebrate': "Real talk - how'd you REALLY do today?",
        'factual': "Objective daily analysis:"
    }
}


COMPLETION_RATING: Dict[str, str] = {
    'excellent': "Outstanding! You're operating at peak performance.",
    'good': "Solid day. You're getting things done.",
    'average': "Not bad, but you're capable of better.",
    'below_average': "Below your potential. What happened?",
    'poor': "This was a weak day. Time for honesty."
}


# ============================================
# PROCRASTINATION DETECTION
# ============================================

PROCRASTINATION_CAUGHT = """I see what's happening here 👀

You're asking about {topic} when you have {urgent_tasks} urgent tasks due {timeframe}.

This is procrastination dressed up as productivity.

Focus on:
{top_priorities}

Then you can explore {topic}.

Sound fair?"""


# ============================================
# ENCOURAGEMENT MESSAGES
# ============================================

ENCOURAGEMENT: Dict[str, list] = {
    'gentle': [
        "You're doing great. Keep going, one step at a time.",
        "Progress, not perfection. You're moving forward.",
        "Be kind to yourself. You're doing better than you think."
    ],
    'direct': [
        "Stop overthinking. Just do it.",
        "You know what needs to be done. Do it.",
        "Excuses don't complete tasks. Action does."
    ],
    'celebrate': [
        "You're CRUSHING it! Keep that energy! 🔥",
        "Look at you go! Momentum is building!",
        "Yes! This is how winners operate!"
    ],
    'factual': [
        "Current progress: On track.",
        "Continue current execution pattern.",
        "Performance is acceptable."
    ]
}


# ============================================
# CONTEXT-AWARE REDIRECTS
# ============================================

NEWS_REDIRECT = {
    'general_news': """Here are today's headlines:
{news}

But real talk - why are you worried about things you can't control?

You have {pending_tasks} tasks that YOU can control.

Master your day first, then catch up on the world.

Deal?""",
    
    'relevant_news': """Here's what's happening in {field}:
{news}

This is actually relevant to your {profession} work.

Anything here you want to save to your notes or research later?"""
}


# ============================================
# ERROR MESSAGES
# ============================================

ERROR_GENERIC = "Hmm, something went wrong on my end. Can you try that again?"

ERROR_NOT_UNDERSTOOD = """I'm not quite sure what you mean.

Try:
• "Remind me to [task]"
• "I need to [task]"  
• "Task X done"
• "OTR: [idea]"
• /help

Or just ask me a question!"""


ERROR_NO_TASKS = "You don't have any tasks yet! Want to add one?"


# ============================================
# HELP MESSAGE
# ============================================

HELP_MESSAGE = """🤖 AI Task Assistant - Help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADDING TASKS (Just talk naturally!):
• "Remind me to call John tomorrow"
• "I need to finish the report by Friday"
• "Buy groceries"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLETING TASKS:
• "task 1 done"
• "finished the report"
• "completed meeting"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SAVING IDEAS (OTR):
• "OTR: Build a mobile app"
• "Idea: Start a podcast"
• "Remember: Research investments"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMANDS:
/tasks - View pending tasks
/ideas - View saved ideas
/stats - Productivity statistics
/help - This message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUESTIONS:
• "What's the weather?"
• "Latest news in [topic]?"
• "How do I [something]?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I understand context and learn your patterns.
Just talk to me naturally! 💬"""


# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_message(message_dict: Dict[str, str], motivation_style: str, **kwargs) -> str:
    """
    Get the appropriate message based on user's motivation style.
    
    Args:
        message_dict: Dictionary of messages by motivation style
        motivation_style: User's preferred motivation style
        **kwargs: Variables to format into the message
    
    Returns:
        Formatted message string
    """
    template = message_dict.get(motivation_style, message_dict.get('factual'))
    return template.format(**kwargs)
