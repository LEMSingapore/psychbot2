# Deploy PsychBot to Render.com (Budget-Friendly!)

This guide shows you how to deploy PsychBot to Render.com for **$7-27/month** (including OpenAI API costs).

## Cost Breakdown

- **Render Starter Plan**: $7/month (512MB RAM, 0.5 CPU)
- **Render Standard Plan**: $25/month (2GB RAM, 1 CPU) - recommended
- **Persistent Disk**: Free (first 1GB)
- **OpenAI API**: ~$0.20-2/month (for ~1000 queries)

**Total: $7-27/month** vs. AWS ECS at $80-100/month!

---

## Prerequisites

1. **GitHub Account** - Your code needs to be on GitHub
2. **Render.com Account** - Sign up at https://render.com (free)
3. **OpenAI Account** - Sign up at https://platform.openai.com
4. **SendGrid Account** - For email (free tier: 100 emails/day)
5. Your **credentials.json** file for Google Calendar

---

## Step 1: Get Your API Keys

### OpenAI API Key

```bash
# 1. Go to https://platform.openai.com/api-keys
# 2. Click "Create new secret key"
# 3. Copy the key (starts with sk-...)
# 4. Save it somewhere safe - you'll need it later

# Pricing: GPT-3.5 Turbo
# - Input: $0.0005 per 1K tokens
# - Output: $0.0015 per 1K tokens
# - ~$0.002 per query (very cheap!)
```

### SendGrid API Key

```bash
# 1. Go to https://app.sendgrid.com/settings/api_keys
# 2. Create API Key with "Mail Send" permission
# 3. Copy the key (starts with SG....)
# 4. Save it for later
```

---

## Step 2: Push Code to GitHub

Your code needs to be on GitHub for Render to deploy it:

```bash
# If you haven't already, push your changes
cd /Users/cheeyoungchang/Projects/psychbot2

# Add the new files
git add requirements.txt
git add src/rag_chain.py
git add src/calendar_utils.py
git add Dockerfile.render
git add render.yaml
git add RENDER_DEPLOYMENT.md

# Commit changes
git commit -m "Switch to OpenAI and prepare for Render deployment"

# Push to GitHub
git push origin main
```

---

## Step 3: Deploy to Render (Two Methods)

### Method A: One-Click Deploy with Blueprint (EASIEST)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Blueprint"**
3. **Connect your GitHub repo**: `LEMSingapore/psychbot2`
4. **Render will detect `render.yaml`** and set everything up automatically
5. **Click "Apply"**

That's it! Now skip to Step 4 to set environment variables.

### Method B: Manual Setup

If the blueprint doesn't work:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub**: Select your `psychbot2` repository
4. **Configure the service**:
   - **Name**: `psychbot`
   - **Region**: Singapore (or closest to you)
   - **Branch**: `main`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./Dockerfile.render`
   - **Plan**: Starter ($7/month) or Standard ($25/month)
5. **Click "Create Web Service"**

---

## Step 4: Set Environment Variables

After creating the service, you need to add your API keys:

1. **In Render Dashboard**, click on your `psychbot` service
2. **Go to "Environment" tab**
3. **Add the following environment variables**:

```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here

# SendGrid API Key (REQUIRED)
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here

# Google Calendar Credentials (REQUIRED)
# Copy the ENTIRE contents of your credentials.json file and paste as one line
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}

# Python environment (automatically set, but you can verify)
PYTHONUNBUFFERED=1
```

**Important Notes:**
- For `GOOGLE_CREDENTIALS_JSON`, open your `credentials.json` file, copy everything, and paste it as the value
- Make sure the JSON is valid (no extra line breaks)
- Click "Save Changes" after adding all variables

4. **Render will automatically redeploy** with the new environment variables

---

## Step 5: Add Persistent Disk (Important!)

The vector database needs to persist between deployments:

1. **In your service dashboard**, go to **"Settings"**
2. **Scroll to "Disks"** section
3. **Click "Add Disk"**:
   - **Name**: `psychbot-data`
   - **Mount Path**: `/app/docs`
   - **Size**: 1 GB (free)
4. **Save Changes**

This ensures your ChromaDB vector database doesn't get deleted on every deploy.

---

## Step 6: Monitor Deployment

1. **Go to "Logs" tab** in Render dashboard
2. **Watch the build process**:
   - Installing dependencies (~2-3 minutes)
   - Running document ingestion
   - Starting uvicorn server
3. **Look for**: `"OpenAI system preloaded and warmed up"`
4. **Your app is live!** at: `https://psychbot.onrender.com`

---

## Step 7: Test Your Deployment

```bash
# Test the API docs
curl https://your-service-name.onrender.com/docs

# Test a chat message
curl -X POST https://your-service-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services do you offer?"}'

# You should get a response like:
# {"response": "Individual $120, Couples $180, Family $200, Group $60, Online $100. Book now?"}
```

---

## Troubleshooting

### Build Fails

**Error: "OPENAI_API_KEY environment variable is required"**
- Solution: Add the OPENAI_API_KEY in Environment tab

**Error: "Vector store directory 'docs' not found"**
- Solution: The ingestion script runs automatically, but check logs to see if it completed
- Try manually running: `python src/ingest.py` in Shell tab

### App Crashes / Out of Memory

**Error: "Process killed"**
- Solution: Upgrade from Starter ($7) to Standard ($25) plan for more RAM
- Go to Settings → Change Plan → Standard

### Slow Responses

**Issue: Queries take 5-10 seconds**
- Render free/starter instances sleep after inactivity
- Solution: Keep app awake with external monitoring (UptimeRobot.com - free)
- Or: Upgrade to Standard plan (doesn't sleep)

### Google Calendar Not Working

**Error: "Invalid credentials"**
- Check that GOOGLE_CREDENTIALS_JSON is set correctly
- Make sure it's valid JSON (no line breaks or extra characters)
- Verify the service account has calendar access

---

## Keeping Your App Awake (Optional)

Render's free/starter plans sleep after 15 minutes of inactivity. To keep it awake:

### Option 1: UptimeRobot (Free)

1. Sign up at https://uptimerobot.com (free)
2. Add a new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-service.onrender.com/docs`
   - **Interval**: 5 minutes
3. UptimeRobot will ping your app every 5 minutes to keep it awake

### Option 2: Upgrade to Standard Plan

Standard plan instances don't sleep and have better performance.

---

## Updating Your App

Every time you push to GitHub, Render automatically rebuilds and deploys:

```bash
# Make your code changes
# Test locally first!

# Commit and push
git add .
git commit -m "Update feature X"
git push origin main

# Render automatically detects the push and redeploys
# Watch progress in the Render dashboard
```

---

## Custom Domain (Optional)

Add your own domain:

1. **In Render dashboard**, go to **Settings**
2. **Click "Add Custom Domain"**
3. **Enter your domain**: `chat.yourdomain.com`
4. **Update your DNS**:
   - Add CNAME record: `chat` → `your-service.onrender.com`
5. **Render automatically provisions SSL certificate** (free!)

---

## Monitoring and Logs

### View Logs
```bash
# In Render dashboard, go to "Logs" tab
# Real-time logs show all requests and errors
```

### Metrics
```bash
# In Render dashboard, go to "Metrics" tab
# Shows CPU, Memory, Network usage
# Helps you decide if you need to upgrade
```

### Set Up Alerts
```bash
# In Render dashboard, go to "Settings"
# Enable "Deploy Notifications"
# Get email/Slack alerts for deploys and failures
```

---

## Cost Optimization Tips

1. **Use Quick Responses**: The `QUICK_RESPONSES` dict in `rag_chain.py` answers common questions without calling OpenAI (free!)

2. **Monitor OpenAI Usage**:
   - Check usage at https://platform.openai.com/usage
   - Set spending limits in OpenAI dashboard

3. **Reduce Token Usage**:
   - Keep responses short (already set to max_tokens=100)
   - Use quick responses for simple queries

4. **Right-size Your Plan**:
   - Start with Starter ($7)
   - Upgrade to Standard ($25) only if needed

**Expected Monthly Costs:**
- 100 queries/day = ~$1/month OpenAI + $7 Render = **$8/month**
- 500 queries/day = ~$5/month OpenAI + $25 Render = **$30/month**
- 1000 queries/day = ~$10/month OpenAI + $25 Render = **$35/month**

Much cheaper than AWS ECS at $80-100/month!

---

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test all features (chat, booking, calendar)
3. Set up custom domain
4. Add monitoring with UptimeRobot
5. Configure backup strategy for persistent disk
6. Set up CI/CD for automated testing before deploy

---

## Support

- **Render Docs**: https://render.com/docs
- **OpenAI Docs**: https://platform.openai.com/docs
- **Issues**: https://github.com/LEMSingapore/psychbot2/issues

Need help? Check the troubleshooting section above or create an issue on GitHub!
