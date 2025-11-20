"""
Configuration file for Thanksgiving Deal Finder
Adjust these settings based on your needs
"""

# API Configuration
OPENAI_MODEL = "gpt-4o"  # or "gpt-4-turbo", "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.7  # 0.0-1.0, lower = more deterministic

# Scheduler Configuration
PRICE_CHECK_INTERVAL_HOURS = 6  # How often to check prices (1-24 hours)
MAX_CONCURRENT_CHECKS = 5  # Max products to check simultaneously

# Deal Search Configuration
MAX_DEALS_PER_SEARCH = 5  # Number of deals to return per search
DEFAULT_TARGET_PRICE = 0.0  # Default target price if not specified

# Alert Configuration
ALERT_PRICE_THRESHOLD = 0.95  # Alert when price is 95% or less of target
ENABLE_TIMING_ALERTS = True  # Send alerts about optimal purchase timing
ENABLE_STOCK_ALERTS = True  # Alert when stock is running low

# Database Configuration
DB_NAME = "deals.db"
DB_TIMEOUT = 10.0  # seconds

# UI Configuration
APP_TITLE = "🦃 Thanksgiving Deal Finder"
PAGE_ICON = "🦃"
LAYOUT = "wide"  # "centered" or "wide"

# Retailers to focus on (for future real scraping)
RETAILERS = [
    "Amazon",
    "Walmart",
    "Target",
    "Best Buy",
    "Costco",
    "B&H Photo",
    "Newegg",
    "eBay"
]

# Product Categories
CATEGORIES = [
    "Electronics",
    "Home Appliances",
    "Clothing",
    "Toys",
    "Gaming",
    "Sports",
    "Books",
    "Beauty"
]

# Timing Analysis Weights
TIMING_ANALYSIS = {
    "days_until_black_friday": 10,  # Current: Nov 16, BF: Nov 29
    "days_until_cyber_monday": 13,  # Current: Nov 16, CM: Dec 2
    "expected_discount_increase": 10,  # Expected % increase on BF/CM
}

# Rate Limiting
API_RATE_LIMIT_DELAY = 2  # seconds between API calls
MAX_SEARCHES_PER_USER_PER_DAY = 50

# Feature Flags (enable/disable features)
FEATURES = {
    "price_history_charts": True,
    "timing_analysis": True,
    "email_notifications": False,  # Not implemented in MVP
    "sms_notifications": False,  # Not implemented in MVP
    "browser_extension": False,  # Not implemented in MVP
    "real_web_scraping": True,  # Use real web scraping (requires scraper.py)
}

# Web Scraping Configuration
SCRAPING_CONFIG = {
    "enabled": True,
    "timeout": 10,  # seconds
    "max_retries": 2,
    "delay_between_retailers": 2,  # seconds (be respectful)
    # Note: User-Agent is auto-detected based on your system (Linux/Mac/Windows)
    # The scraper automatically uses Chrome user agent matching your platform
}

# Deployment Configuration
DEPLOYMENT = {
    "environment": "development",  # "development" or "production"
    "debug_mode": True,
    "log_level": "INFO",  # "DEBUG", "INFO", "WARNING", "ERROR"
}
