# 🚀 KNOWDEX Deployment Guide

This guide walks you through deploying KNOWDEX to Render (and other platforms).

## 📋 Table of Contents

1. [Render Deployment (Recommended)](#render-deployment)
2. [Deploying Both Frontend and Backend](#deploying-both)
3. [Environment Variables](#environment-variables)
4. [Post-Deployment](#post-deployment)
5. [Alternative Platforms](#alternative-platforms)

---

## 🎯 Render Deployment (Recommended)

Render is perfect for deploying KNOWDEX because it offers:
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Git-based deployments
- ✅ Easy environment variable management

### Option 1: Deploy Chainlit Frontend Only

This gives you the beautiful chat interface (recommended for demos/portfolio).

#### Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Add Chainlit frontend"
git push origin main
```

#### Step 2: Create New Web Service on Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your KNOWDEX repository

#### Step 3: Configure the Service

Fill in these settings:

```yaml
Name: knowdex-chat
Region: Choose nearest to your users
Branch: main
Root Directory: (leave blank)

Build Command:
pip install -r requirements.txt

Start Command:
chainlit run chainlit_app.py -h 0.0.0.0 -p $PORT

Instance Type: Free (or paid for better performance)
```

#### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `BRAVE_API_KEY` | Your Brave Search API key |
| `PYTHON_VERSION` | 3.11 |

#### Step 5: Deploy!

Click **"Create Web Service"**

Render will:
1. Clone your repository
2. Install dependencies
3. Start the Chainlit app
4. Give you a URL like `https://knowdex-chat.onrender.com`

**First deployment takes ~5 minutes**

---

### Option 2: Deploy FastAPI Backend Only

This gives you a REST API for programmatic access.

#### Configure the Service

```yaml
Name: knowdex-api
Region: Choose nearest to your users
Branch: main
Root Directory: (leave blank)

Build Command:
pip install -r requirements.txt

Start Command:
uvicorn backend.main:app --host 0.0.0.0 --port $PORT

Instance Type: Free (or paid for better performance)
```

Add the same environment variables as Option 1.

**API Documentation will be available at**: `https://your-app.onrender.com/docs`

---

## 🔄 Deploying Both Frontend and Backend

You have two approaches:

### Approach A: Two Separate Services (Recommended)

Deploy twice on Render:

1. **Service 1**: Chainlit frontend (for users)
   - URL: `https://knowdex-chat.onrender.com`
   
2. **Service 2**: FastAPI backend (for API access)
   - URL: `https://knowdex-api.onrender.com`

**Pros**: 
- Independent scaling
- Can update one without affecting the other
- Clear separation of concerns

**Cons**: 
- Uses 2 free tier slots
- Slightly more complex setup

### Approach B: Single Service with Docker

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run Chainlit (you can switch to FastAPI if needed)
CMD ["chainlit", "run", "chainlit_app.py", "-h", "0.0.0.0", "-p", "8000"]
```

Create a `render.yaml`:

```yaml
services:
  - type: web
    name: knowdex
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: BRAVE_API_KEY
        sync: false
```

Deploy:
1. Push code to GitHub
2. On Render, select **"Blueprint"** instead of **"Web Service"**
3. Connect your repo
4. Add environment variables
5. Deploy!

---

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Where to Get It |
|----------|-------------|-----------------|
| `OPENAI_API_KEY` | OpenAI API key | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `BRAVE_API_KEY` | Brave Search API key | [brave.com/search/api](https://brave.com/search/api) |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./knowdex_local.db` | Database connection string |
| `PYTHON_VERSION` | `3.11` | Python version to use |
| `PORT` | `8000` | Port to run on (auto-set by Render) |

---

## ✅ Post-Deployment Checklist

After deployment, verify everything works:

### 1. Check Service Status

- [ ] Service shows "Live" status on Render dashboard
- [ ] Logs show "Application startup complete"
- [ ] No error messages in logs

### 2. Test the Application

**For Chainlit Frontend:**
- [ ] Visit your deployment URL
- [ ] See the welcome message
- [ ] Ask a test question
- [ ] Verify you get a response with sources

**For FastAPI Backend:**
- [ ] Visit `https://your-app.onrender.com/docs`
- [ ] Try the `/api/research` endpoint
- [ ] Verify streaming works

### 3. Monitor Performance

```bash
# Check logs on Render dashboard
# Look for:
- Response times
- Error rates
- Memory usage
```

### 4. Set Up Auto-Deploy (Optional)

On Render:
1. Go to your service settings
2. Under **"Build & Deploy"**
3. Enable **"Auto-Deploy"**

Now every push to main automatically deploys! 🎉

---

## 🚨 Troubleshooting

### Issue: Build Fails

**Symptoms**: Deployment fails during build phase

**Solution**:
```bash
# Check your requirements.txt is valid
pip install -r requirements.txt

# Verify Python version in render.yaml or settings
```

### Issue: App Crashes on Startup

**Symptoms**: Service starts then immediately crashes

**Solution**:
1. Check logs on Render dashboard
2. Verify environment variables are set correctly
3. Ensure database can be created (SQLite works on Render)

**Common fixes**:
```bash
# Make sure you're using correct start command
# For Chainlit:
chainlit run chainlit_app.py -h 0.0.0.0 -p $PORT

# For FastAPI:
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### Issue: API Keys Not Working

**Symptoms**: "API key not found" errors in logs

**Solution**:
1. Go to Render dashboard → Your service → Environment
2. Verify `OPENAI_API_KEY` and `BRAVE_API_KEY` are set
3. Restart service manually

### Issue: Database Errors

**Symptoms**: SQLite database errors

**Solution**:
Render's free tier has ephemeral storage. For production:

1. **Use Render's PostgreSQL** (recommended):
   - Create a PostgreSQL database on Render
   - Update `DATABASE_URL` environment variable
   - Update `backend/database.py` if needed

2. **Or use persistent disk** (paid tier):
   - Enable persistent disk in service settings
   - Mount at `/app/data`
   - Update database path

### Issue: Slow Performance on Free Tier

**Symptoms**: First request takes 30+ seconds

**Solution**:
This is normal! Render's free tier spins down after inactivity.

Options:
1. Upgrade to paid tier ($7/month) for always-on service
2. Keep free tier and accept cold starts
3. Use a ping service to keep it warm (may violate ToS)

### Issue: Out of Memory

**Symptoms**: Service crashes with memory errors

**Solution**:
```bash
# Upgrade instance type on Render dashboard
# Free tier: 512MB RAM
# Paid tier: 2GB+ RAM
```

---

## 🌐 Alternative Platforms

### Heroku

```bash
# Create Procfile
echo "web: chainlit run chainlit_app.py -h 0.0.0.0 -p \$PORT" > Procfile

# Deploy
heroku create knowdex
git push heroku main
heroku config:set OPENAI_API_KEY=your_key
heroku config:set BRAVE_API_KEY=your_key
```

### Railway

1. Import project from GitHub
2. Add environment variables
3. Set start command: `chainlit run chainlit_app.py -h 0.0.0.0 -p $PORT`
4. Deploy!

### Vercel (Serverless)

⚠️ **Not recommended** for KNOWDEX because:
- Streaming responses are harder to implement
- 10-second timeout on hobby tier
- Better suited for static sites

### AWS/Google Cloud/Azure

Use Docker deployment:

```bash
# Build image
docker build -t knowdex .

# Run locally to test
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e BRAVE_API_KEY=your_key \
  knowdex

# Push to cloud registry and deploy
# (Platform-specific instructions)
```

---

## 📊 Cost Estimates

### Render

| Tier | Price | Features |
|------|-------|----------|
| Free | $0/month | 750 hours/month, sleeps after 15min |
| Starter | $7/month | Always on, 512MB RAM |
| Standard | $25/month | 2GB RAM, better performance |

### API Costs

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| OpenAI GPT-4 | 1000 requests | ~$3-5/month |
| Brave Search | 1000 queries | Free (2000/month limit) |

**Total Monthly Cost**: ~$10-15 for always-on deployment

---

## 🎯 Production Best Practices

### 1. Use PostgreSQL Instead of SQLite

```bash
# On Render, create a PostgreSQL database
# Update DATABASE_URL in environment variables
postgresql://user:password@host:port/database
```

### 2. Set Up Monitoring

Use Render's built-in monitoring or:
- [Sentry](https://sentry.io) for error tracking
- [DataDog](https://datadoghq.com) for performance monitoring

### 3. Implement Rate Limiting

```python
# Add to chainlit_app.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### 4. Add Authentication (Optional)

For private deployments:

```python
# In .chainlit config
[project]
user_env = ["PASSWORD"]

# Implement custom auth
@cl.password_auth_callback
def auth(username: str, password: str):
    # Your auth logic
    return True
```

### 5. Set Up CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Trigger Render deploy
        run: curl https://api.render.com/deploy/...
```

---

## 📞 Need Help?

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Chainlit Docs**: [docs.chainlit.io](https://docs.chainlit.io)
- **Open an Issue**: [GitHub Issues](https://github.com/your-repo/issues)

---

**Happy Deploying! 🚀**

