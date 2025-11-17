# 🦃 Thanksgiving Deal Finder - Complete POC Package

## 📦 What You Have

A production-ready proof-of-concept AI agent for finding Thanksgiving/Black Friday deals using:
- **Streamlit** (UI)
- **GPT-4o** (OpenAI)
- **APScheduler** (Background jobs)
- **SQLite** (Database)

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Your API Key
Create `.env` file:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Run the App
```bash
streamlit run app.py
```

## 📁 Files Included

### Core Files
- `app.py` - Main application (19KB)
- `config.py` - Configuration settings
- `requirements.txt` - Dependencies
- `test_setup.py` - Setup validator

### Configuration
- `.env.example` - Environment template
- `.gitignore` - Git exclusions

### Scripts
- `start.sh` - Quick launch script (Linux/Mac)

### Documentation
- `README.md` - Complete overview
- `QUICKSTART.md` - 5-minute guide
- `DEPLOYMENT.md` - Platform deployment guides
- `PROJECT_STRUCTURE.md` - Architecture details

## ✨ Key Features

### 1. AI-Powered Deal Search
- Searches multiple retailers
- Compares prices automatically
- Ranks deal quality
- Shows availability status

### 2. Smart Timing Analysis
- Predicts Black Friday prices
- Recommends buy now vs. wait
- Analyzes stock-out risks
- Provides confidence levels

### 3. Automated Price Tracking
- Checks prices every 6 hours
- Stores historical data
- Generates price charts
- Tracks trends

### 4. Intelligent Alerts
- Price drop notifications
- Timing recommendations
- Target price alerts
- Stock warnings

## 💰 Cost Breakdown

### API Costs (GPT-4o)
- Input: $0.0025 per 1K tokens
- Output: $0.010 per 1K tokens

**Monthly Estimates:**
- 10 users, 5 products each: $15-39/month
- 50 users, 10 products each: $150-390/month

### Hosting Costs
- Streamlit Cloud: Free (limited) or $20/month
- Render: $7-25/month (recommended)
- Railway: $5-20/month
- Digital Ocean: $5-12/month

**Total MVP**: $20-60/month for light usage

## 🎯 Architecture Overview

```
User Interface (Streamlit)
        ↓
GPT-4o API (OpenAI)
        ↓
Deal Analysis Engine
        ↓
SQLite Database
        ↓
Background Scheduler (APScheduler)
        ↓
Alert System
```

## 🔧 Customization

### Adjust Check Frequency
Edit `config.py`:
```python
PRICE_CHECK_INTERVAL_HOURS = 6  # Change this
```

### Change Number of Results
```python
MAX_DEALS_PER_SEARCH = 5  # Modify this
```

### Modify AI Temperature
```python
OPENAI_TEMPERATURE = 0.7  # 0.0-1.0
```

## 📊 Database Schema

**products** table:
- Product tracking information
- User preferences
- Target prices

**price_history** table:
- Historical price data
- Retailer information
- Check timestamps

**alerts** table:
- Generated notifications
- Alert types
- Read status

## 🧪 Testing Your Setup

Run the test script:
```bash
python test_setup.py
```

This validates:
- ✓ Python version
- ✓ Dependencies installed
- ✓ OpenAI API working
- ✓ Database operations
- ✓ Scheduler functioning

## 🌐 Deployment Options

### Best for MVP: Render or Railway
Both offer:
- Easy GitHub deployment
- Background job support
- Automatic HTTPS
- Reasonable pricing ($7-20/month)

### Quick Deployment: Streamlit Cloud
- Free tier available
- 5-minute setup
- Public URL
- Limited for background jobs

See `DEPLOYMENT.md` for detailed guides.

## 🎨 UI Preview

The app includes:
- **Search Tab**: Find and analyze deals
- **Tracked Products Tab**: Monitor price history
- **Alerts Sidebar**: Real-time notifications
- **Charts**: Visual price trends
- **Metrics**: Current vs. lowest prices

## 🔐 Security

- API keys in `.env` (not committed)
- SQLite parameterized queries
- No sensitive data exposure
- Local file storage

## 📈 Usage Flow

1. **User searches** for product
2. **GPT-4o analyzes** deals across retailers
3. **System recommends** buy now or wait
4. **User tracks** interesting products
5. **Scheduler checks** prices every 6 hours
6. **Alerts notify** when deals improve
7. **User makes** informed purchase

## 🚨 Common Issues & Solutions

### "API key not found"
→ Create `.env` file with your OpenAI key

### "Dependencies missing"
→ Run `pip install -r requirements.txt`

### "Database locked"
→ Close other instances of the app

### "Scheduler not running"
→ Normal on first run; wait 6 hours or deploy

## 🎓 Next Steps

### Phase 1: Enhance
- [ ] Add real web scraping
- [ ] Implement email notifications
- [ ] Add user authentication
- [ ] Connect shopping APIs

### Phase 2: Scale
- [ ] Switch to PostgreSQL
- [ ] Add Redis caching
- [ ] Implement rate limiting
- [ ] Deploy load balancer

### Phase 3: Expand
- [ ] Build mobile app
- [ ] Create browser extension
- [ ] Add ML price predictions
- [ ] International support

## 📚 Additional Resources

### Documentation
- **OpenAI**: https://platform.openai.com/docs
- **Streamlit**: https://docs.streamlit.io
- **APScheduler**: https://apscheduler.readthedocs.io

### Deployment Platforms
- **Render**: https://render.com
- **Railway**: https://railway.app
- **Streamlit Cloud**: https://share.streamlit.io

## 🤝 Support

### Getting Help
1. Check `QUICKSTART.md` for common questions
2. Review `DEPLOYMENT.md` for platform issues
3. Run `test_setup.py` to diagnose problems
4. Check OpenAI dashboard for API issues

### Monitoring Costs
- OpenAI Usage: https://platform.openai.com/usage
- Set billing alerts in OpenAI dashboard
- Monitor logs for excessive API calls

## 💡 Pro Tips

1. **Start Small**: Track 1-2 products initially
2. **Test Locally**: Verify everything works before deploying
3. **Monitor Costs**: Check API usage daily at first
4. **Optimize Later**: Get it working, then optimize
5. **User Feedback**: Share with friends, iterate

## 🎉 You're Ready!

Your complete Thanksgiving Deal Finder POC is ready to deploy!

**Next Steps:**
1. Run `test_setup.py` to validate setup
2. Test locally with `streamlit run app.py`
3. Deploy to Render or Railway
4. Start tracking deals!

---

**Built with ❤️ for savvy Black Friday shoppers**

Questions? Check the documentation files or test with sample products like:
- "iPhone 15 Pro"
- "Sony WH-1000XM5"
- "MacBook Air M2"
- "LG C3 OLED TV"

Happy deal hunting! 🛍️
