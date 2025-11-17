# Deployment Guide - Thanksgiving Deal Finder

## Quick Deployment Comparison

| Platform | Cost | Setup Time | Background Jobs | Best For |
|----------|------|------------|----------------|----------|
| Streamlit Cloud | Free-$20/mo | 5 min | Limited | Quick demo |
| Render | $7-25/mo | 10 min | ✅ Full support | MVP/Production |
| Railway | $5-20/mo | 10 min | ✅ Full support | MVP/Production |
| Digital Ocean | $5-12/mo | 15 min | ✅ Full support | Production |
| Heroku | $7-25/mo | 10 min | ✅ Full support | Traditional |

## 1. Streamlit Community Cloud (Fastest)

### Pros
- Free tier available
- Easiest deployment
- Auto-deploys from GitHub
- No server management

### Cons
- Limited background scheduling on free tier
- App sleeps after inactivity (free tier)
- Limited resources

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

2. **Deploy on Streamlit**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Select your GitHub repo
- Choose `app.py` as the main file

3. **Add Secrets**
- In app settings, go to "Secrets"
- Add:
```toml
OPENAI_API_KEY = "sk-your-key-here"
```

4. **Deploy!**
- Click "Deploy"
- Your app will be live at `https://[your-app].streamlit.app`

### Important Notes
- Free tier may have scheduling limitations
- Consider paid tier ($20/mo) for better performance
- App URL is public unless you upgrade

---

## 2. Render (Recommended for MVP)

### Pros
- Background jobs work perfectly
- Automatic HTTPS
- Free PostgreSQL database
- GitHub auto-deploy
- Better uptime than Streamlit free

### Cons
- Requires payment for web services
- Slightly more complex setup

### Steps

1. **Create Render Account**
- Go to [render.com](https://render.com)
- Sign up with GitHub

2. **Create New Web Service**
- Dashboard → New → Web Service
- Connect your GitHub repo
- Select the repo

3. **Configure Service**

**Name**: `thanksgiving-deals`

**Environment**: `Python 3`

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

**Instance Type**: Starter ($7/mo)

4. **Environment Variables**
- Click "Environment" tab
- Add:
  - Key: `OPENAI_API_KEY`
  - Value: `sk-your-key-here`

5. **Deploy**
- Click "Create Web Service"
- Wait 3-5 minutes for deployment

6. **Access Your App**
- URL: `https://thanksgiving-deals.onrender.com`

### Render-Specific Configuration

Create `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: thanksgiving-deals
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
    envVars:
      - key: OPENAI_API_KEY
        sync: false
```

---

## 3. Railway

### Pros
- Very simple setup
- Usage-based pricing
- Excellent for background jobs
- Auto-detects Streamlit

### Steps

1. **Create Account**
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

2. **Create New Project**
- Dashboard → "New Project"
- Select "Deploy from GitHub repo"
- Choose your repo

3. **Configure**
- Railway auto-detects Python
- Add environment variables:
  - `OPENAI_API_KEY`: your-key

4. **Custom Start Command** (if needed)
- Settings → Start Command:
```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

5. **Deploy**
- Railway automatically deploys
- Get your URL from the deployment

### Railway-Specific Files

Create `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 4. Digital Ocean App Platform

### Pros
- Reliable infrastructure
- Good for scaling
- Flat pricing
- Full Docker support

### Steps

1. **Create Account**
- Go to [digitalocean.com](https://digitalocean.com)
- Sign up

2. **Create App**
- Apps → Create App
- Connect GitHub
- Select repo

3. **Configure App**

**Name**: `thanksgiving-deals`

**Source**: Your GitHub repo

**Build Command**:
```bash
pip install -r requirements.txt
```

**Run Command**:
```bash
streamlit run app.py --server.port=8080 --server.address=0.0.0.0
```

**HTTP Port**: `8080`

4. **Environment Variables**
- Add `OPENAI_API_KEY`

5. **Choose Plan**
- Basic: $5/mo
- Professional: $12/mo (recommended)

6. **Deploy**
- Click "Create Resources"

### App Spec (Optional)

Create `.do/app.yaml`:

```yaml
name: thanksgiving-deals
services:
  - name: web
    github:
      repo: your-username/your-repo
      branch: main
      deploy_on_push: true
    build_command: pip install -r requirements.txt
    run_command: streamlit run app.py --server.port=8080 --server.address=0.0.0.0
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: OPENAI_API_KEY
        value: ${OPENAI_API_KEY}
        type: SECRET
```

---

## 5. Docker Deployment (Any Platform)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.git
.gitignore
.env
deals.db
*.db
```

### Build and Run

```bash
# Build
docker build -t thanksgiving-deals .

# Run
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your-key \
  thanksgiving-deals
```

### Deploy to Cloud with Docker

**Google Cloud Run**:
```bash
gcloud run deploy thanksgiving-deals \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**AWS ECS** / **Azure Container Apps**: Similar process

---

## Environment Variables Setup

For all platforms, you need these environment variables:

```bash
# Required
OPENAI_API_KEY=sk-your-actual-key-here

# Optional (for future features)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## Post-Deployment Checklist

- [ ] App is accessible via URL
- [ ] OpenAI API key is working (test a search)
- [ ] Database is being created
- [ ] Price checks are running (check after 6 hours)
- [ ] Alerts are being generated
- [ ] No errors in logs

---

## Monitoring & Logs

### Streamlit Cloud
- Dashboard → Your app → Logs

### Render
- Dashboard → Your service → Logs tab

### Railway
- Dashboard → Your project → Deployments → Logs

### Digital Ocean
- Apps → Your app → Runtime Logs

---

## Troubleshooting Deployment Issues

### Issue: App won't start

**Check**:
1. All dependencies in `requirements.txt`
2. Correct start command
3. Port configuration
4. Environment variables set

### Issue: Background jobs not running

**Solution**: Verify platform supports long-running processes
- Streamlit Cloud free tier: Limited
- Render/Railway/DO: Full support

### Issue: Database errors

**Check**:
1. SQLite file permissions
2. Persistent storage configured
3. Database timeout settings

### Issue: High API costs

**Optimize**:
1. Reduce check frequency
2. Implement caching
3. Limit products per user
4. Add rate limiting

---

## Scaling Considerations

### For 100+ Users

1. **Switch to PostgreSQL**
   - Render/Railway/DO offer managed PostgreSQL
   - Better for concurrent access

2. **Add Redis for Caching**
   - Cache search results
   - Rate limiting

3. **Separate Worker Service**
   - Run scheduler as separate service
   - Use job queue (Celery + Redis)

4. **Load Balancing**
   - Multiple app instances
   - Session state in Redis

---

## Cost Optimization Tips

1. **Choose the right check frequency**
   - 6 hours: Good balance
   - 12 hours: Lower costs
   - 1 hour: Higher costs

2. **Implement caching**
   - Cache product searches for 1 hour
   - Reduce duplicate API calls

3. **Set user limits**
   - Max products per user
   - Max searches per day

4. **Use cheaper models for simple tasks**
   - GPT-3.5-turbo for formatting
   - GPT-4o for complex analysis

---

## Next Steps After Deployment

1. **Monitor Performance**
   - Check logs daily
   - Track API costs
   - Monitor user feedback

2. **Collect User Feedback**
   - Add feedback form
   - Track feature usage
   - Iterate based on data

3. **Add Analytics**
   - Google Analytics
   - Mixpanel
   - Custom event tracking

4. **Scale Gradually**
   - Start with small user base
   - Optimize before scaling
   - Monitor costs closely

---

Need help with a specific platform? Check the platform's documentation or reach out for support!
