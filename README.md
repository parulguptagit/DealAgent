# 🦃 Thanksgiving Deal Finder - AI Agent MVP

An AI-powered deal finder that helps users find the best Thanksgiving, Black Friday, and Cyber Monday deals using GPT-4o.

## 🎯 Features

- **AI-Powered Deal Search**: Uses GPT-4o to find and analyze deals across multiple retailers
- **Smart Timing Analysis**: Predicts whether to buy now or wait for Black Friday/Cyber Monday
- **Automated Price Tracking**: Background scheduler checks prices every 6 hours
- **Intelligent Alerts**: Get notified when prices drop below your target
- **Price History**: View trends and make data-driven decisions
- **User-Friendly Interface**: Clean Streamlit UI with real-time updates

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Model**: GPT-4o (OpenAI)
- **Scheduling**: APScheduler (background jobs)
- **Database**: SQLite (lightweight, file-based)
- **Web Scraping**: BeautifulSoup4 + Requests

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (get one at https://platform.openai.com/)

## 🚀 Setup Instructions

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd thanksgiving-deal-finder
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Run the App Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📦 Deployment Options

### Option 1: Streamlit Community Cloud (Free, Easiest)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repo
4. Add your `OPENAI_API_KEY` in Secrets section:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```
5. Deploy!

**Note**: Free tier may have limitations with background scheduling. For production, consider paid options.

### Option 2: Render (Recommended for MVP)

1. Create account at [render.com](https://render.com)
2. Create new "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variables in dashboard
6. Deploy!

**Cost**: $7-25/month (better for background jobs)

### Option 3: Railway

1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Add environment variables
4. Railway auto-detects and deploys

**Cost**: $5-20/month (usage-based)

### Option 4: Digital Ocean App Platform

1. Create account at [digitalocean.com](https://digitalocean.com)
2. Go to App Platform → Create App
3. Connect GitHub repo
4. Configure environment variables
5. Deploy

**Cost**: $5-12/month

## 📊 Usage Guide

### 1. Search for Deals

- Enter product name (e.g., "iPhone 15 Pro", "Sony WH-1000XM5")
- Set your target price
- Click "Find Deals"
- Review AI-powered deal analysis and timing recommendations

### 2. Track Products

- Click "Track This Product" after searching
- The system will monitor prices automatically every 6 hours
- You'll receive alerts when:
  - Price drops below your target
  - Better timing is predicted for Black Friday/Cyber Monday

### 3. Monitor Alerts

- Check the sidebar for new alerts
- View price history in the "Tracked Products" tab
- Make informed decisions based on trends

## 🔧 Configuration

### Adjust Price Check Frequency

Edit `app.py` line ~200:

```python
scheduler.add_job(
    func=check_all_products,
    trigger=IntervalTrigger(hours=6),  # Change this value
    ...
)
```

Options:
- `hours=6` - Check every 6 hours (default, good for MVP)
- `hours=12` - Check twice daily (lower costs)
- `hours=1` - Check hourly (higher costs, more responsive)

### Modify Number of Deals Retrieved

Edit `app.py` line ~340:

```python
deals = search_deals_with_ai(product_search, max_results=5)  # Change this
```

## 💰 Cost Estimates

### GPT-4o API Costs

Based on typical usage:
- **Light usage** (10 users, 5 products): $15-39/month
- **Medium usage** (50 users, 10 products): $150-390/month

### Hosting Costs

- **Streamlit Cloud**: Free (limited) or $20/month
- **Render**: $7-25/month
- **Railway**: $5-20/month
- **Digital Ocean**: $5-12/month

**Total MVP Cost**: $20-60/month for light usage

## 🎨 Customization Ideas

### Add Real Web Scraping

Replace the simulated deal search with actual scrapers:

```python
# Example: Add Amazon scraper
import requests
from bs4 import BeautifulSoup

def scrape_amazon(product_name):
    # Implement Amazon API or scraping
    pass
```

### Add Email Notifications

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(user_email, message):
    # Implement email sending
    pass
```

### Add User Authentication

```python
import streamlit_authenticator as stauth

# Add login system
authenticator = stauth.Authenticate(...)
```

### Connect to Real Shopping APIs

- Amazon Product Advertising API
- Walmart Open API
- Best Buy API
- Target RedSky API

## 🐛 Troubleshooting

### Issue: APScheduler not running in Streamlit Cloud

**Solution**: Streamlit Cloud's free tier may pause apps. Consider:
1. Using paid Streamlit tier
2. Moving to Render/Railway for better background job support
3. Using external cron service (GitHub Actions, Zapier)

### Issue: OpenAI API rate limits

**Solution**:
1. Add delays between requests (`time.sleep(2)`)
2. Implement exponential backoff
3. Cache common queries
4. Upgrade to higher API tier

### Issue: Database locked errors

**Solution**:
```python
# Add timeout to SQLite connections
conn = sqlite3.connect('deals.db', timeout=10.0)
```

## 📈 Future Enhancements

- [ ] Real-time web scraping with Playwright/Selenium
- [ ] Email/SMS notifications via Twilio
- [ ] User authentication and multi-user support
- [ ] Historical price analytics and predictions
- [ ] Browser extension for one-click tracking
- [ ] Mobile app with React Native
- [ ] Integration with shopping APIs
- [ ] Price drop prediction ML models
- [ ] Comparison across international retailers

## 🤝 Contributing

This is a proof-of-concept MVP. Feel free to fork and enhance!

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 🙋 Support

For issues or questions:
1. Check the troubleshooting section
2. Review OpenAI API documentation
3. Check Streamlit documentation

## 🎓 Learning Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Streamlit Docs](https://docs.streamlit.io)
- [APScheduler Docs](https://apscheduler.readthedocs.io/)

---

**Built with ❤️ for savvy Black Friday shoppers!**
