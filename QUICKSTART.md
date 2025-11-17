# Quick Start Guide 🚀

## 5-Minute Setup

### Step 1: Get Your OpenAI API Key
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

### Step 2: Install & Configure
```bash
# Clone the repository
git clone <your-repo-url>
cd thanksgiving-deal-finder

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any text editor
```

### Step 3: Run the App
```bash
streamlit run app.py
```

That's it! The app will open at http://localhost:8501

---

## First Time Use

### 1. Search for a Product
- Enter product name: "iPhone 15 Pro"
- Set target price: $900
- Click "Find Deals"

### 2. Review Results
- See current deals from multiple retailers
- Check AI timing recommendation
- View expected Black Friday discounts

### 3. Track Products
- Click "Track This Product"
- Get automatic price checks every 6 hours
- Receive alerts when prices drop

### 4. Monitor Alerts
- Check sidebar for new alerts
- View price history in "Tracked Products" tab
- Make informed purchase decisions

---

## Key Features at a Glance

| Feature | What It Does |
|---------|--------------|
| **AI Deal Search** | Finds best current prices across retailers |
| **Timing Analysis** | Tells you if you should buy now or wait |
| **Price Tracking** | Monitors prices automatically every 6 hours |
| **Smart Alerts** | Notifies when prices hit your target |
| **Price History** | Shows trends to help decision-making |

---

## Common Questions

**Q: How often are prices checked?**  
A: Every 6 hours by default. You can adjust this in `config.py`

**Q: How much does it cost to run?**  
A: ~$15-39/month for GPT-4o API costs (light usage)

**Q: Can I track unlimited products?**  
A: Yes, but more products = higher API costs

**Q: Does it work for international retailers?**  
A: The MVP focuses on US retailers, but can be customized

**Q: Is my data private?**  
A: Yes, everything is stored locally in SQLite

---

## Troubleshooting

### App won't start
```bash
# Check Python version (need 3.8+)
python3 --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### API errors
- Verify your OpenAI API key in `.env`
- Check you have API credits at https://platform.openai.com/
- Ensure key starts with `sk-`

### Database errors
```bash
# Delete and recreate database
rm deals.db
# App will recreate on next run
```

### Scheduler not running
- Background jobs work better on deployed apps
- For local testing, scheduler starts automatically
- Check logs for any errors

---

## Configuration Tips

### Reduce API Costs
Edit `config.py`:
```python
PRICE_CHECK_INTERVAL_HOURS = 12  # Instead of 6
MAX_DEALS_PER_SEARCH = 3  # Instead of 5
```

### Increase Check Frequency
```python
PRICE_CHECK_INTERVAL_HOURS = 1  # Check every hour
```

### Change Temperature (AI creativity)
```python
OPENAI_TEMPERATURE = 0.5  # More consistent (0.0-1.0)
```

---

## Usage Examples

### Example 1: Electronics
```
Product: "Sony WH-1000XM5 Headphones"
Target: $300
Result: Found at $328 at Amazon, wait for BF (expected $280)
```

### Example 2: Appliances
```
Product: "Instant Pot Duo 7-in-1"
Target: $60
Result: Found at $79 at Target, BUY NOW (unlikely to drop more)
```

### Example 3: Gaming
```
Product: "PlayStation 5"
Target: $450
Result: Found at $499 at Best Buy, HIGH RISK (stock may run out)
```

---

## Next Steps

1. **Deploy to Cloud**
   - See `DEPLOYMENT.md` for detailed guides
   - Recommended: Render or Railway for MVP

2. **Customize**
   - Edit `config.py` for your preferences
   - Adjust retailers in configuration
   - Modify check frequency

3. **Add Features**
   - Email notifications (SMTP setup)
   - Real web scraping
   - User authentication

4. **Monitor Costs**
   - Check OpenAI usage dashboard
   - Set up billing alerts
   - Optimize API calls

---

## Support & Resources

- **OpenAI Docs**: https://platform.openai.com/docs
- **Streamlit Docs**: https://docs.streamlit.io
- **APScheduler**: https://apscheduler.readthedocs.io/

---

## Tips for Best Results

1. **Be Specific**: "iPhone 15 Pro 256GB" better than "iPhone"
2. **Set Realistic Targets**: Check current prices first
3. **Track Early**: Start tracking weeks before Black Friday
4. **Check Multiple Products**: Compare similar items
5. **Review Price History**: Look for patterns before buying

---

## Sample Products to Try

- Electronics: "iPhone 15 Pro", "Samsung Galaxy S24", "AirPods Pro"
- TVs: "LG C3 OLED 55", "Samsung QN90C", "Sony A95K"
- Laptops: "MacBook Air M2", "Dell XPS 13", "ThinkPad X1"
- Gaming: "PS5", "Xbox Series X", "Nintendo Switch OLED"
- Appliances: "Instant Pot", "Ninja Air Fryer", "Dyson V15"

---

Happy deal hunting! 🦃🛍️
