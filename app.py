import streamlit as st
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import time
import hashlib
from dotenv import load_dotenv
load_dotenv()

try:
    # Try Streamlit secrets first (for cloud deployment)
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    # Fall back to environment variable (for local development)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_user_id():
    """Generate unique user ID based on session"""
    # On Streamlit Cloud, each user gets a unique session ID
    # We'll use that to create a unique user ID
    if 'user_id' not in st.session_state:
        # Create a unique identifier for this session
        session_id = st.session_state.get('_session_id', None)
        if session_id is None:
            # Generate a random ID if no session ID
            import uuid
            session_id = str(uuid.uuid4())
            st.session_state._session_id = session_id
        
        # Create user_id from session_id
        st.session_state.user_id = hashlib.md5(session_id.encode()).hexdigest()[:16]
    
    return st.session_state.user_id

# Import our custom scraper
try:
    from scraper import scrape_product_deals
    SCRAPING_ENABLED = True
except ImportError:
    SCRAPING_ENABLED = False
    print("Warning: Scraper module not available, will use AI-generated deals only")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def parse_json_response(json_string):
    """
    Parse JSON from GPT response, handling markdown code blocks
    """
    json_string = json_string.strip()
    
    # Remove markdown code blocks if present
    if json_string.startswith("```json"):
        json_string = json_string[7:]
    elif json_string.startswith("```"):
        json_string = json_string[3:]
    
    if json_string.endswith("```"):
        json_string = json_string[:-3]
    
    json_string = json_string.strip()
    
    return json.loads(json_string)

# Database setup
def init_db():
    conn = sqlite3.connect('deals.db', check_same_thread=False)
    c = conn.cursor()
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  product_name TEXT,
                  target_price REAL,
                  created_at TIMESTAMP,
                  alert_enabled INTEGER DEFAULT 1)''')
    
    # Price history table
    c.execute('''CREATE TABLE IF NOT EXISTS price_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  product_id INTEGER,
                  retailer TEXT,
                  price REAL,
                  url TEXT,
                  checked_at TIMESTAMP,
                  FOREIGN KEY (product_id) REFERENCES products(id))''')
    
    # Alerts table
    c.execute('''CREATE TABLE IF NOT EXISTS alerts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  product_id INTEGER,
                  alert_type TEXT,
                  message TEXT,
                  created_at TIMESTAMP,
                  read INTEGER DEFAULT 0,
                  FOREIGN KEY (product_id) REFERENCES products(id))''')
    
    conn.commit()
    conn.close()

# Database operations
def add_product(user_id, product_name, target_price):
    conn = sqlite3.connect('deals.db')
    c = conn.cursor()
    c.execute("INSERT INTO products (user_id, product_name, target_price, created_at) VALUES (?, ?, ?, ?)",
              (user_id, product_name, target_price, datetime.now()))
    product_id = c.lastrowid
    conn.commit()
    conn.close()
    return product_id

def get_user_products(user_id):
    conn = sqlite3.connect('deals.db')
    df = pd.read_sql_query("SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC", 
                           conn, params=(user_id,))
    conn.close()
    return df

def get_price_history(product_id):
    conn = sqlite3.connect('deals.db')
    df = pd.read_sql_query("SELECT * FROM price_history WHERE product_id = ? ORDER BY checked_at DESC", 
                           conn, params=(product_id,))
    conn.close()
    return df

def add_price_record(product_id, retailer, price, url):
    conn = sqlite3.connect('deals.db')
    c = conn.cursor()
    c.execute("INSERT INTO price_history (product_id, retailer, price, url, checked_at) VALUES (?, ?, ?, ?, ?)",
              (product_id, retailer, price, url, datetime.now()))
    conn.commit()
    conn.close()

def create_alert(product_id, alert_type, message):
    conn = sqlite3.connect('deals.db')
    c = conn.cursor()
    c.execute("INSERT INTO alerts (product_id, alert_type, message, created_at) VALUES (?, ?, ?, ?)",
              (product_id, alert_type, message, datetime.now()))
    conn.commit()
    conn.close()

def get_unread_alerts(user_id):
    conn = sqlite3.connect('deals.db')
    query = """
    SELECT a.*, p.product_name 
    FROM alerts a 
    JOIN products p ON a.product_id = p.id 
    WHERE p.user_id = ? AND a.read = 0 
    ORDER BY a.created_at DESC
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def mark_alert_read(alert_id):
    conn = sqlite3.connect('deals.db')
    c = conn.cursor()
    c.execute("UPDATE alerts SET read = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()


# AI-powered deal finder using GPT-4o with real web scraping
def search_deals_with_ai(product_name, max_results=5):
    """Search for deals using real web scraping first, then AI enhancement"""   

    # Try real web scraping first
    if SCRAPING_ENABLED:
        try:
            st.info("🔍 Searching real retailers (Amazon, Walmart, Best Buy)...")
            real_deals = scrape_product_deals(product_name, max_results=max_results)           

            if real_deals and len(real_deals) > 0:
                st.success(f"✅ Found {len(real_deals)} real deals from live retailers!")
                return real_deals
            else:
                st.warning("⚠️ No results from web scraping, using AI analysis...")
        except Exception as e:
            st.warning(f"⚠️ Web scraping unavailable: {str(e)[:100]}. Using AI analysis...")    

    # Fallback to AI-generated deals (for demo or when scraping fails)

    st.info("🤖 Using AI to analyze deals...")
    prompt = f"""You are a deal-finding assistant. Generate realistic Thanksgiving/Black Friday deal information for: {product_name}

Return a JSON array with {max_results} deals from different retailers. Each deal should have:
- retailer: store name (Amazon, Walmart, Target, Best Buy, etc.)
- price: current price (realistic numbers)
- original_price: original price before discount
- discount_percentage: percentage off
- url: example URL (use example.com/product)
- availability: "In Stock" or "Limited Stock"
- deal_quality: "Excellent", "Good", or "Fair"

Make the prices realistic and varied. Include a mix of good and average deals.

Return ONLY valid JSON, no other text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful shopping assistant that returns only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        deals_json = response.choices[0].message.content
        print(deals_json)
        deals = parse_json_response(deals_json)
        print(deals)
        return deals
    except json.JSONDecodeError as e:
        st.error(f"Error parsing deals JSON: {str(e)}")
        st.error(f"Response was: {deals_json[:200]}...")
        return []
    except Exception as e:
        st.error(f"Error searching deals: {str(e)}")
        return []

def analyze_deal_timing(product_name, current_prices):
    """Use GPT-4o to analyze if waiting for Black Friday/Cyber Monday would be better"""
    
    avg_price = sum([d['price'] for d in current_prices]) / len(current_prices) if current_prices else 0
    
    prompt = f"""Analyze whether a buyer should purchase {product_name} now (Thanksgiving week) or wait for Black Friday/Cyber Monday.

Current average price: ${avg_price:.2f}
Current date context: Mid-November, Thanksgiving week

Consider:
1. Historical pricing patterns for this product category
2. Typical Black Friday/Cyber Monday discounts
3. Stock availability risks
4. Product category trends

Return a JSON object with:
{{
    "recommendation": "buy_now" or "wait",
    "confidence": "high", "medium", or "low",
    "reasoning": "brief explanation",
    "expected_bf_discount": estimated percentage (0-50),
    "risk_level": "low", "medium", or "high" (for stock-outs)
}}

Return ONLY valid JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a shopping strategy expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        analysis_json = response.choices[0].message.content
        analysis = parse_json_response(analysis_json)
        return analysis
    except Exception as e:
        st.error(f"Error analyzing timing: {str(e)}")
        return None

# Background job to check prices
def check_all_products():
    """Background job that checks prices for all tracked products"""
    conn = sqlite3.connect('deals.db')
    c = conn.cursor()
    
    # Get all products with alerts enabled
    c.execute("SELECT id, product_name, target_price FROM products WHERE alert_enabled = 1")
    products = c.fetchall()
    conn.close()
    
    for product_id, product_name, target_price in products:
        try:
            # Search for current deals
            deals = search_deals_with_ai(product_name, max_results=3)
            
            if deals:
                # Save best deal
                best_deal = min(deals, key=lambda x: x['price'])
                add_price_record(product_id, best_deal['retailer'], 
                               best_deal['price'], best_deal['url'])
                
                # Check if price is below target
                if best_deal['price'] <= target_price:
                    message = f"🎉 Price Alert! {product_name} is now ${best_deal['price']:.2f} at {best_deal['retailer']} (Target: ${target_price:.2f})"
                    create_alert(product_id, "price_alert", message)
                
                # Check timing recommendation
                analysis = analyze_deal_timing(product_name, deals)
                if analysis and analysis['recommendation'] == 'wait' and analysis['confidence'] == 'high':
                    message = f"⏳ Timing Alert! Consider waiting for {product_name}. {analysis['reasoning']}"
                    create_alert(product_id, "timing_alert", message)
            
            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"Error checking product {product_id}: {str(e)}")
            continue

# Initialize scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    # Run every 6 hours (adjust as needed for production)
    scheduler.add_job(
        func=check_all_products,
        trigger=IntervalTrigger(minutes=5),
        id='price_check_job',
        name='Check product prices',
        replace_existing=True
    )
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Thanksgiving Deal Finder",
        page_icon="🦃",
        initial_sidebar_state="auto",
        layout="wide"
    )
    
    # Initialize database
    init_db()
    
    # Initialize scheduler (only once)
    if 'scheduler_started' not in st.session_state:
        start_scheduler()
        st.session_state.scheduler_started = True
    
    # Session state for user ID (in production, use real auth)
    if 'user_id' not in st.session_state:
        st.session_state.user_id = get_user_id()
    
    # Display user session info (optional, for debugging)
    with st.sidebar:
        st.caption(f"Session ID: {st.session_state.user_id[:8]}...")
    
    # Header
    st.title("🦃 Thanksgiving Deal Finder")
    st.markdown("*AI-powered deal tracking for Black Friday & Cyber Monday*")
    
    # Sidebar - Alerts
    with st.sidebar:
        st.header("🔔 Alerts")
        alerts = get_unread_alerts(st.session_state.user_id)
        
        if not alerts.empty:
            st.metric("Unread Alerts", len(alerts))
            for _, alert in alerts.iterrows():
                with st.expander(f"{alert['product_name']}", expanded=True):
                    st.write(alert['message'])
                    st.caption(f"{alert['created_at']}")
                    if st.button("Mark as Read", key=f"alert_{alert['id']}"):
                        mark_alert_read(alert['id'])
                        st.rerun()
        else:
            st.info("No new alerts")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Search Deals", "📊 Tracked Products", "ℹ️ About"])
    
    with tab1:
        st.header("Search for Deals")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            product_search = st.text_input("What product are you looking for?", 
                                          placeholder="e.g., iPhone 15, Sony WH-1000XM5, LG OLED TV")
        with col2:
            target_price = st.number_input("Target Price ($)", min_value=0.0, value=0.0, step=10.0)
        
        col1, col2 = st.columns([1, 1])

        with col1:

            search_button = st.button("🔍 Find Deals", type="primary", use_container_width=True)

        with col2:

            clear_button = st.button("🔄 Clear Search", use_container_width=True)

        

        # Clear search functionality

        if clear_button:

            if 'last_search' in st.session_state:

                del st.session_state.last_search

            st.rerun()

        

        if search_button:
            if product_search:
                with st.spinner("Searching for the best deals..."):
                    # Search for deals
                    deals = search_deals_with_ai(product_search, max_results=5)
                    
                    if deals:
                        # Store in session state so it persists after button clicks

                        st.session_state.last_search = {
                            'product': product_search,
                            'target_price': target_price,
                            'deals': deals

                        }
                    else:

                        st.error("No deals found. Please try again.")
            else:
                st.warning("Please enter a product name") # Display results if we have a last search

        if 'last_search' in st.session_state and st.session_state.last_search:
            search_data = st.session_state.last_search
            deals = search_data['deals']
            product_search = search_data['product']
            target_price = search_data['target_price']
          
            if deals:
                st.success(f"Found {len(deals)} deals!")

                # Display deals

                st.subheader("Current Deals")

                for i, deal in enumerate(deals):
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])                      
                        with col1:
                            st.markdown(f"**{deal['retailer']}**")
                            # Show product name if available (from real scraping)
                            if 'product_name' in deal and deal['product_name']:
                                st.caption(f"📦 {deal['product_name'][:80]}...")
                            st.caption(f"🔗 {deal['url'][:50]}...")                      

                        with col2:
                            st.metric("Price", f"${deal['price']:.2f}", 
                                    f"-{deal['discount_percentage']}%")                      

                        with col3:
                            quality_color = {"Excellent": "🟢", "Good": "🟡", "Fair": "🟠"}
                            st.write(f"{quality_color.get(deal['deal_quality'], '⚪')} {deal['deal_quality']}")
                            st.caption(deal['availability'])                        

                        with col4:
                            if i == 0:
                                st.success("🏆 Best Price!")
                            # Show if it's a real deal
                            if deal['url'] and not 'example.com' in deal['url']:
                                st.info("✨ Live Deal")    

                        st.divider()                

                # Timing analysis

                st.subheader("Should You Buy Now or Wait?")
                with st.spinner("Analyzing timing strategy..."):
                    analysis = analyze_deal_timing(product_search, deals)                   

                    if analysis:
                        col1, col2 = st.columns(2)                       

                        with col1:
                            if analysis['recommendation'] == 'wait':
                                st.warning("💡 **Recommendation: Wait for Black Friday/Cyber Monday**")
                            else:
                                st.success("💡 **Recommendation: Buy Now**")                           

                            st.write(analysis['reasoning'])

                            st.caption(f"Confidence: {analysis['confidence'].title()}")                        

                        with col2:

                            st.metric("Expected BF Discount", f"{analysis['expected_bf_discount']}%")

                            st.metric("Stock-out Risk", analysis['risk_level'].title())                

                # Track product

                st.divider()
                if st.button("📌 Track This Product"):
                    product_id = add_product(st.session_state.user_id, product_search, target_price)                   

                    # Save initial price data

                    best_deal = min(deals, key=lambda x: x['price'])
                    add_price_record(product_id, best_deal['retailer'], 
                                   best_deal['price'], best_deal['url'])                    

                    st.success(f"✅ Now tracking {product_search}! You'll receive alerts when better deals appear.")

                    st.info("💡 Check the 'Tracked Products' tab to see your tracked items.")
    
    with tab2:
        st.header("Your Tracked Products")
        
        products = get_user_products(st.session_state.user_id)
        
        if not products.empty:
            for _, product in products.iterrows():
                with st.expander(f"📦 {product['product_name']}", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Target Price:** ${product['target_price']:.2f}")
                        st.caption(f"Tracking since: {product['created_at']}")
                    
                    with col2:
                        alert_status = "🟢 Active" if product['alert_enabled'] else "🔴 Paused"
                        st.write(f"Alerts: {alert_status}")
                    
                    # Price history
                    price_history = get_price_history(product['id'])
                    
                    if not price_history.empty:
                        st.subheader("Price History")
                        
                        # Create price chart
                        chart_data = price_history[['checked_at', 'price', 'retailer']].copy()
                        chart_data['checked_at'] = pd.to_datetime(chart_data['checked_at'])
                        
                        st.line_chart(chart_data.set_index('checked_at')['price'])
                        
                        # Show latest prices
                        st.dataframe(
                            price_history[['retailer', 'price', 'checked_at']].head(5),
                            use_container_width=True
                        )
                        
                        # Current best price
                        best_price = price_history['price'].min()
                        current_price = price_history.iloc[0]['price']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Current Best Price", f"${current_price:.2f}")
                        with col2:
                            st.metric("Lowest Price Seen", f"${best_price:.2f}")
                    else:
                        st.info("No price history yet. Price checks run every 6 hours.")
        else:
            st.info("You're not tracking any products yet. Search for deals in the 'Search Deals' tab!")
    
    with tab3:
        st.header("About This App")
        
        st.markdown("""
        ### 🎯 Features
        - **AI-Powered Deal Finding**: Uses GPT-4o to search and analyze deals across multiple retailers
        - **Smart Timing Analysis**: Predicts whether to buy now or wait for Black Friday/Cyber Monday
        - **Price Tracking**: Automatically monitors prices every 6 hours
        - **Intelligent Alerts**: Get notified when prices drop below your target
        - **Historical Analysis**: View price trends and make informed decisions
        
        ### 🛠️ Technology Stack
        - **Frontend**: Streamlit
        - **AI Model**: GPT-4o (OpenAI)
        - **Scheduling**: APScheduler
        - **Database**: SQLite
        
        ### 📝 How to Use
        1. Search for a product you want to buy
        2. Review current deals and timing recommendations
        3. Track products you're interested in
        4. Receive alerts when better deals appear
        5. Make informed purchase decisions!
        
        ### ⚙️ Configuration
        - Price checks run every 6 hours
        - Alerts are generated for prices below target or timing changes
        - All data is stored locally in SQLite
        
        ### 💡 Tips
        - Set realistic target prices based on current deals
        - Check multiple retailers for the same product
        - Pay attention to timing recommendations
        - Act quickly on "Excellent" deals with "High" confidence
        """)
        
        st.divider()
        st.caption("Built with ❤️ using Streamlit + GPT-4o")

if __name__ == "__main__":
    main()
