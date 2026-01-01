# 🤖 AI Task Assistant
**By OkayYouGotMe**

> A truly conversational AI assistant that helps people stay productive through natural conversation, brutal honesty, and smart task management.

---

## 🌟 What Makes This Special?

This isn't just another task bot. This is a **conversation partner** that:

- 🧠 **Understands context** - Remembers your conversations and learns your patterns
- 💬 **Talks naturally** - No robotic commands, just normal conversation
- 📊 **Tells the truth** - Brutally honest assessments of your productivity
- 🎯 **Simplifies overwhelm** - Breaks down big tasks into manageable steps
- ⏰ **Never lets you slack** - Persistent reminders that keep nagging until you respond
- 🎨 **Adapts to you** - Matches your profession, goals, and motivation style

---

## ✨ Features

### For Users:
- **Smart Onboarding** - 6 questions to understand who you are and what you need
- **Natural Conversation** - Talk like you would to a friend, AI understands intent
- **Task Breakdown** - Big overwhelming task? AI breaks it into bite-sized wins
- **Persistent Reminders** - Set priority level, AI nags until you confirm completion
- **Brutal Assessments** - Daily, weekly, monthly, quarterly honest feedback
- **External Data** - Weather, news, web search - ask anything
- **Goal Tracking** - Monitors progress toward your big goals
- **Pattern Recognition** - Spots your procrastination triggers and redirects you

### For Developers:
- **Clean Code** - Heavily commented, easy to understand
- **Modular Design** - Each feature is separate, easy to update
- **Multi-User Ready** - Built for unlimited users from day one
- **Database Backed** - PostgreSQL for speed and reliability
- **Easy Configuration** - Change settings without touching code
- **Well Documented** - Every function explains what it does and why

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Railway account (free)
- Telegram Bot Token
- Claude API Key

### Setup (15 Minutes)

1. **Clone or Download This Code**
   ```bash
   git clone your-repo-url
   cd ai-task-assistant-v2
   ```

2. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Deploy to Railway**
   - Push code to GitHub
   - Connect Railway to your repo
   - Railway auto-detects and deploys
   - Bot goes live!

Detailed instructions in `docs/DEPLOYMENT.md`

---

## 📁 Project Structure

```
ai-task-assistant-v2/
│
├── README.md                 ← You are here
├── requirements.txt          ← Python dependencies
├── main.py                   ← Application entry point
├── Procfile                  ← Railway deployment config
├── railway.json              ← Railway settings
│
├── config/                   ← All configuration
│   ├── settings.py           ← Easy settings (change here!)
│   └── database.py           ← Database connection
│
├── database/                 ← Database layer
│   ├── models.py             ← Data tables (User, Task, etc.)
│   └── operations.py         ← Database functions
│
├── bot/                      ← Telegram interface
│   ├── telegram_bot.py       ← Main bot logic
│   ├── handlers.py           ← Message handling
│   └── messages.py           ← All bot messages (easy to edit!)
│
├── ai/                       ← AI brain
│   ├── claude_engine.py      ← Main AI integration
│   ├── intent_analyzer.py    ← Understands what user wants
│   ├── task_breakdown.py     ← Breaks down big tasks
│   └── response_generator.py ← Creates humanized responses
│
├── features/                 ← Main features
│   ├── onboarding.py         ← User setup questionnaire
│   ├── reminders.py          ← Persistent reminder system
│   ├── assessments.py        ← Brutal honest reviews
│   ├── simplification.py     ← Daily task organization
│   └── integrations.py       ← Weather, news, web search
│
├── utils/                    ← Helper functions
│   ├── time_parser.py        ← Parse "tomorrow at 4pm"
│   ├── pattern_detector.py   ← Find behavior patterns
│   └── logger.py             ← Logging system
│
└── docs/                     ← Documentation
    ├── DEPLOYMENT.md         ← How to deploy
    ├── FEATURES.md           ← Feature details
    └── DEVELOPMENT.md        ← For developers
```

---

## 🎯 How Users Interact

### Example Conversation:

```
User: "Good morning"

Bot: "Good morning Alex! ☀️ Hope you slept well!
     
     Today in Amsterdam: 50°F, partly cloudy
     
     You have 5 tasks for today. Let me simplify:
     
     QUICK WINS (30 min total):
     ✅ Reply to supplier email (5 min)
     ✅ Submit timesheet (10 min)
     
     BIG FOCUS (needs concentration):
     🎯 Patient charts (60 min)
     Best time: 10 AM when you're sharpest
     
     Ready to crush it? 💪"

User: "I need to prepare for Friday's presentation but don't know where to start"

Bot: "Let's break this down so you don't get overwhelmed:
     
     PRESENTATION PREP - BREAKDOWN:
     1. ✅ Outline content (15 min)
     2. ✅ Create slides (45 min)
     3. ✅ Practice run (20 min)
     4. ✅ Final polish (10 min)
     
     Total: ~90 minutes
     
     Want me to add all 4 as separate tasks?
     Or track the whole thing as one?"

User: "Add them all"

Bot: "✅ Done! Added 4 tasks for Friday presentation.
     
     Pro tip: Do outline TODAY while it's fresh in your mind.
     Then slides tomorrow when you have focus time.
     
     Sound good?"
```

---

## ⚙️ Configuration

All settings in one place: `config/settings.py`

```python
# Timing
DAILY_ASSESSMENT_TIME = "22:00"  # When to send daily review
HOURLY_CHECKIN_START = 9         # Start hourly check-ins
HOURLY_CHECKIN_END = 23          # End hourly check-ins

# AI Behavior
BRUTAL_HONESTY_LEVEL = "high"    # Options: low, medium, high
AI_TEMPERATURE = 0.7             # Creativity level (0-1)

# Reminders
CRITICAL_REMINDER_INTERVALS = [0, 5, 10, 15, 20]  # Nag every 5 min
IMPORTANT_REMINDER_INTERVALS = [0, 15, 30]        # Nag every 15 min

# Easy to change - no code knowledge needed!
```

---

## 🔧 For Developers

### Adding a New Feature

1. Create new file in `features/`:
   ```python
   # features/my_new_feature.py
   class MyNewFeature:
       """Clear description of what this does"""
       
       def do_something(self, user_id):
           # Your code here
           pass
   ```

2. Import in main:
   ```python
   from features.my_new_feature import MyNewFeature
   ```

3. Done! No need to touch existing code.

### Modifying Bot Messages

All messages in `bot/messages.py` - just edit the strings!

### Database Changes

All models in `database/models.py` - clearly documented.

---

## 📊 Database Schema

### Tables:
- **users** - User profiles and preferences
- **tasks** - All user tasks
- **conversations** - Chat history for context
- **reminders** - Scheduled reminders
- **ideas** - OTR ideas/notes
- **completions** - Completed task history
- **assessments** - Daily/weekly/monthly reviews

Full schema documentation in `docs/DATABASE.md`

---

## 🐛 Troubleshooting

### Bot Not Responding?
- Check Railway logs
- Verify environment variables
- Ensure database is connected

### Messages Not Sending?
- Check Telegram bot token
- Verify user has started conversation with bot

### Database Errors?
- Check PostgreSQL connection
- Verify migrations ran successfully

More help in `docs/TROUBLESHOOTING.md`

---

## 📝 License

Free to use and modify for personal and commercial use.

---

## 🙏 Credits

**Created by:** OkayYouGotMe
**AI Integration:** Claude by Anthropic
**Platform:** Telegram

---

## 💬 Support

Questions? Issues? Want to add features?

Check the docs folder or review the code - everything is heavily commented!

---

**Built with ❤️ for people who want to get stuff done.**
