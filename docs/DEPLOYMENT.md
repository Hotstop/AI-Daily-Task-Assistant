# 🚀 Deployment Guide

## Easy 3-Step Deployment to Railway

### Step 1: Prepare Your Code

1. **Download this project** to your computer
2. **Edit `.env.example`** and rename to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   CLAUDE_API_KEY=your_key_here
   ```
3. **Don't worry about DATABASE_URL** - Railway will add it automatically

### Step 2: Upload to GitHub

**Option A: Using GitHub Website (Easiest)**

1. Go to github.com
2. Click "New Repository"
3. Name it: `ai-task-assistant`
4. Click "Create"
5. Click "uploading an existing file"
6. Drag the whole `ai-task-assistant-v2` folder
7. Click "Commit changes"

**Option B: Using Git Command Line**

```bash
cd ai-task-assistant-v2
git init
git add .
git commit -m "Initial commit"
git remote add origin your-github-url
git push -u origin main
```

### Step 3: Deploy to Railway

1. **Go to Railway Dashboard** (railway.app)

2. **Click "New Project"**

3. **Click "Deploy from GitHub repo"**

4. **Select your repo** (`ai-task-assistant`)

5. **Add PostgreSQL Database:**
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically connects it to your app
   - DATABASE_URL is set automatically!

6. **Add Environment Variables:**
   - Click on your project
   - Go to "Variables" tab
   - Add:
     - `TELEGRAM_BOT_TOKEN` = your token
     - `CLAUDE_API_KEY` = your key
   - DATABASE_URL is already there!

7. **Deploy!**
   - Railway detects Python automatically
   - Installs requirements.txt
   - Runs `python main.py`
   - Bot goes LIVE! 🎉

### Step 4: Test It Works

1. **Open Telegram**
2. **Search for your bot** (@YourBotUsername)
3. **Send:** `/start`
4. **You should see the welcome message!**

---

## Troubleshooting

### "Bot not responding"
- Check Railway logs (click on deployment → "Logs")
- Verify TELEGRAM_BOT_TOKEN is correct
- Make sure bot is not running elsewhere

### "Database errors"
- Verify PostgreSQL is added to project
- Check DATABASE_URL exists in variables
- Railway should auto-connect them

### "Claude API errors"
- Verify CLAUDE_API_KEY is correct
- Check you have API credits
- Check console.anthropic.com for usage

---

## Monitoring

**Check Logs:**
- Railway Dashboard → Your Project → Logs
- See real-time what's happening

**Check Database:**
- Railway Dashboard → PostgreSQL → Data
- View tables and data

---

## Updating the Bot

After making code changes:

```bash
git add .
git commit -m "Updated feature X"
git push
```

Railway auto-deploys! ✨

---

## Cost Estimate

- **Railway:** $5-10/month (first $5 free)
- **Claude API:** $3-8/month (depends on usage)
- **PostgreSQL:** Included with Railway
- **Telegram:** Free forever

**Total:** ~$8-18/month for unlimited users

---

## Support

If stuck, check:
1. Railway logs
2. This guide
3. Code comments (everything is documented!)

Bot should "just work" once environment variables are set! 🚀
