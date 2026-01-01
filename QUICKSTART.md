# 🚀 QUICK START GUIDE

## Get Your Bot Running in 15 Minutes!

### Step 1: Get Your Credentials (5 minutes)

#### A) Telegram Bot Token
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Follow prompts to create bot
5. Copy the token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### B) Claude API Key
1. Go to https://console.anthropic.com
2. Sign up / Log in
3. Go to "API Keys"
4. Create new key
5. Copy it (looks like: `sk-ant-api03-...`)

---

### Step 2: Deploy to Railway (5 minutes)

#### A) Upload Code to GitHub
**Easy Way (GitHub Website):**
1. Go to github.com
2. Click "New Repository"
3. Name it: `ai-task-assistant`
4. Make it Private
5. Click "uploading an existing file"
6. Drag entire `ai-task-assistant-v2` folder
7. Click "Commit changes"

#### B) Deploy to Railway
1. Go to https://railway.app
2. Click "Login" → Sign up with GitHub
3. Click "New Project"
4. Click "Deploy from GitHub repo"
5. Select `ai-task-assistant`
6. Railway will start deploying!

#### C) Add PostgreSQL Database
1. In your Railway project, click "New"
2. Click "Database" → "Add PostgreSQL"
3. Done! Railway auto-connects it

#### D) Add Environment Variables
1. Click on your project card
2. Click "Variables" tab
3. Click "New Variable"
4. Add these:

```
TELEGRAM_BOT_TOKEN = your_bot_token_here
CLAUDE_API_KEY = your_claude_key_here
```

That's it! `DATABASE_URL` is already there from PostgreSQL!

5. Railway will automatically redeploy

---

### Step 3: Test It! (5 minutes)

1. **Open Telegram**
2. **Search for your bot** (the @username you created)
3. **Send:** `/start`

You should see:
```
Hey! Welcome to AI Task Assistant!

I'm your AI productivity partner. I'll help you:
• Stay on top of your tasks
• Break down overwhelming projects
• Give you brutally honest feedback
• Keep you accountable to your goals

Let's get you set up! Takes just 2 minutes.

Ready? Reply 'yes' to start!
```

4. **Reply:** `yes`
5. **Follow the onboarding** (6 questions)
6. **Done!** Your bot is live! 🎉

---

### Step 4: Invite Users!

Now anyone can:
1. Search for your bot on Telegram
2. Send `/start`
3. Complete onboarding
4. Start using it!

**Each user gets:**
- Personal profile
- Private tasks & ideas
- Custom motivation style
- Separate assessments

---

## 🔧 Troubleshooting

### Bot not responding?
1. Check Railway logs (click project → "Logs")
2. Verify `TELEGRAM_BOT_TOKEN` is correct
3. Make sure PostgreSQL is added

### "Configuration error"?
- Check environment variables in Railway
- Make sure both keys are added
- No quotes around values

### Database errors?
- Verify PostgreSQL is added to project
- Check `DATABASE_URL` exists in variables
- Railway should auto-connect them

---

## 💰 Cost

**Month 1:** FREE (Railway $5 credit)
**After:** ~$8-13/month
- Railway: $5-10/month
- Claude API: $3-8/month (usage-based)
- PostgreSQL: Included

For UNLIMITED users! 🚀

---

## 📊 Monitoring

**Check Logs:**
- Railway → Your Project → "Logs" tab
- See what bot is doing in real-time

**Check Database:**
- Railway → PostgreSQL → "Data" tab
- View users, tasks, etc.

---

## 🎉 You're Done!

Your bot is now:
- ✅ Running 24/7
- ✅ Handling unlimited users
- ✅ Storing data securely
- ✅ Using AI for smart responses

**Next:**
- Share bot with friends/team
- Customize messages in `bot/messages.py`
- Add new features easily

---

## ❓ Need Help?

Check the main README.md for:
- Full documentation
- Code structure
- Feature details
- Advanced configuration

**Enjoy your AI assistant!** 🤖✨
