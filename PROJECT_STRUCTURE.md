# Project Structure

```
thanksgiving-deal-finder/
│
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── test_setup.py              # Setup validation script
│
├── .env.example               # Environment variables template
├── .env                       # Your environment variables (create this)
├── .gitignore                 # Git ignore rules
│
├── start.sh                   # Quick start script (Linux/Mac)
├── deals.db                   # SQLite database (auto-created)
│
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick start guide
├── DEPLOYMENT.md             # Deployment instructions
│
└── (optional)
    ├── Dockerfile            # Docker configuration
    ├── docker-compose.yml    # Docker Compose setup
    ├── render.yaml           # Render deployment config
    └── railway.json          # Railway deployment config
```

## File Descriptions

### Core Application Files

**app.py** (Main Application)
- Streamlit UI implementation
- Database operations (SQLite)
- OpenAI API integration
- APScheduler setup for background jobs
- Deal search and analysis logic
- Alert system

**config.py** (Configuration)
- API settings (model, temperature)
- Scheduler settings (check frequency)
- Database configuration
- UI customization
- Feature flags
- Deployment settings

**requirements.txt**
- streamlit: Web framework
- openai: GPT-4o integration
- requests: HTTP requests
- beautifulsoup4: Web scraping (future)
- pandas: Data manipulation
- apscheduler: Background scheduling
- python-dotenv: Environment variables

### Setup & Testing

**test_setup.py**
- Validates environment setup
- Tests OpenAI API connection
- Checks dependencies
- Tests database operations
- Verifies scheduler

**start.sh**
- Automated startup script
- Creates virtual environment
- Installs dependencies
- Starts the application

### Configuration

**.env.example** (Template)
```
OPENAI_API_KEY=your_key_here
```

**.env** (Your Secrets)
```
OPENAI_API_KEY=sk-actual-key
```

**.gitignore**
- Prevents committing secrets
- Excludes database files
- Ignores Python cache
- Excludes virtual environments

### Documentation

**README.md**
- Project overview
- Features list
- Setup instructions
- Usage guide
- Cost estimates
- Technology stack

**QUICKSTART.md**
- 5-minute setup guide
- Common questions
- Troubleshooting
- Usage examples
- Tips and tricks

**DEPLOYMENT.md**
- Platform-by-platform guides
- Streamlit Cloud
- Render
- Railway
- Digital Ocean
- Docker setup
- Cost comparisons

### Database Structure

**deals.db** (SQLite)

Tables:
1. **products**
   - id: Product identifier
   - user_id: User identifier
   - product_name: Product name
   - target_price: User's target price
   - created_at: Tracking start date
   - alert_enabled: Alert status

2. **price_history**
   - id: Record identifier
   - product_id: Links to products
   - retailer: Store name
   - price: Current price
   - url: Product URL
   - checked_at: Check timestamp

3. **alerts**
   - id: Alert identifier
   - product_id: Links to products
   - alert_type: Type of alert
   - message: Alert message
   - created_at: Alert timestamp
   - read: Read status

## Data Flow

```
User Search
    ↓
GPT-4o API (Deal Search)
    ↓
Display Results
    ↓
GPT-4o API (Timing Analysis)
    ↓
User Tracks Product
    ↓
Saved to Database
    ↓
Background Scheduler (Every 6 hours)
    ↓
GPT-4o API (Price Check)
    ↓
Update Database
    ↓
Generate Alerts (if triggered)
    ↓
Display in UI
```

## API Integration

### OpenAI GPT-4o Calls

1. **Deal Search**
   - Input: Product name
   - Output: JSON array of deals
   - Tokens: ~2,000 input, ~500 output

2. **Timing Analysis**
   - Input: Product name + current prices
   - Output: JSON recommendation
   - Tokens: ~1,500 input, ~300 output

3. **Background Price Checks**
   - Frequency: Every 6 hours
   - Per product: ~2,000 tokens
   - Scheduled via APScheduler

## State Management

### Session State (Streamlit)
- user_id: Demo user identifier
- scheduler_started: Scheduler status

### Database State
- All persistent data in SQLite
- No Redis/external cache in MVP
- File-based storage

## Background Jobs

### APScheduler
- Runs in background thread
- Interval: Every 6 hours (configurable)
- Job: check_all_products()
- Graceful shutdown on app exit

### Price Check Flow
1. Query all tracked products
2. For each product:
   - Search for deals (GPT-4o)
   - Save best price
   - Check if below target
   - Analyze timing
   - Generate alerts if needed
3. Rate limiting between calls

## Security Considerations

### API Keys
- Stored in .env (not committed)
- Loaded via python-dotenv
- Never exposed in UI

### Database
- SQLite with parameterized queries
- No SQL injection risk
- Local file storage

### User Data
- Demo mode: single user
- Production: add authentication
- No sensitive data collected

## Performance

### Optimization Strategies
1. **Caching**: Store recent searches
2. **Rate Limiting**: 2s delay between API calls
3. **Batch Processing**: Check multiple products
4. **Efficient Queries**: Indexed database
5. **Lazy Loading**: Load data as needed

### Resource Usage
- **Memory**: ~100-200 MB
- **CPU**: Low (except during API calls)
- **Storage**: ~10 MB + database growth
- **Network**: API calls only

## Scalability

### Current Limits
- Single-user demo mode
- SQLite (good for <100 users)
- File-based storage
- No load balancing

### Scale to 100+ Users
1. PostgreSQL instead of SQLite
2. Redis for caching
3. Separate worker service
4. User authentication
5. Rate limiting per user
6. Load balancer

### Scale to 1000+ Users
1. Microservices architecture
2. Kubernetes orchestration
3. Managed database (RDS)
4. CDN for static assets
5. Message queue (RabbitMQ)
6. Monitoring (Datadog/New Relic)

## Monitoring & Debugging

### Logs
- Streamlit logs: Terminal output
- Database logs: SQLite journal
- Scheduler logs: APScheduler output

### Debugging Tips
1. Check terminal for errors
2. Verify .env file exists
3. Test API key with test_setup.py
4. Review database with SQLite browser
5. Monitor API usage on OpenAI dashboard

### Health Checks
- Test OpenAI connection
- Verify database writes
- Check scheduler jobs
- Monitor API costs

## Future Enhancements

### Phase 1 (MVP+)
- [ ] Real web scraping (Playwright)
- [ ] Email notifications (SMTP)
- [ ] User authentication
- [ ] Multiple users support

### Phase 2 (Growth)
- [ ] Shopping API integrations
- [ ] SMS notifications (Twilio)
- [ ] Mobile app
- [ ] Browser extension

### Phase 3 (Scale)
- [ ] ML price predictions
- [ ] International retailers
- [ ] Social features
- [ ] Marketplace

## Development Workflow

### Local Development
```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test
python test_setup.py

# Run
streamlit run app.py

# Debug
streamlit run app.py --logger.level=debug
```

### Deployment
```bash
# Test locally first
streamlit run app.py

# Push to GitHub
git add .
git commit -m "Deploy"
git push

# Deploy to platform (auto)
# or manual: see DEPLOYMENT.md
```

## Contributing

### Code Style
- PEP 8 for Python
- Type hints where helpful
- Docstrings for functions
- Comments for complex logic

### Testing
- Run test_setup.py before commits
- Test search functionality
- Verify alerts work
- Check mobile responsive

### Pull Requests
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit PR with description

---

This project structure is designed for rapid MVP development while maintaining clean architecture for future scaling.
