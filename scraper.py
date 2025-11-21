"""
Web Scraper Module for Thanksgiving Deal Finder
Streamlit-optimized version with persistent Chrome driver
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote_plus, urljoin
import re
from typing import List, Dict, Optional
import platform
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
import atexit
from urllib.parse import unquote
import os

def get_chrome_driver_path():
    """Get Chrome/Chromium driver path based on environment"""
    # On Streamlit Cloud, chromium is installed via packages.txt
    if os.path.exists('/usr/bin/chromium-driver'):
        return '/usr/bin/chromium-driver'
    elif os.path.exists('/usr/bin/chromedriver'):
        return '/usr/bin/chromedriver'
    else:
        # Local development
        return None  # Will use default

def get_chrome_binary_path():
    """Get Chrome/Chromium binary path based on environment"""
    # On Streamlit Cloud, use system chromium
    if os.path.exists('/usr/bin/chromium'):
        return '/usr/bin/chromium'
    elif os.path.exists('/usr/bin/chromium-browser'):
        return '/usr/bin/chromium-browser'
    elif os.path.exists('/usr/bin/google-chrome'):
        return '/usr/bin/google-chrome'
    else:
        return None  # Use default

class DealScraper:
    """Scrapes product deals from various retailers using Selenium"""
    
    # Class-level driver to be shared across instances
    _driver = None
    _driver_lock = False
    
    def __init__(self, use_selenium=True, headless=True):
        """
        Initialize the scraper
        
        Args:
            use_selenium: If True, use Selenium for all requests. If False, fall back to requests library
            headless: If True, run Chrome in headless mode
        """
        self.use_selenium = use_selenium
        self.headless = headless
        
        # Detect platform and use appropriate user agent
        self.user_agent = self._get_user_agent()
        
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Keep session as backup if selenium fails
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get_chrome_driver(self):
        """Get or create Chrome driver instance (cloud-compatible)"""
        if DealScraper._driver is None:
            try:
                options = Options()
                
                if self.headless:
                    options.add_argument('--headless=new')  # Use new headless mode
                
                # Essential Chrome options for stability
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-gpu')
                options.add_argument(f'user-agent={self.user_agent}')
                
                chrome_binary = get_chrome_binary_path()
                if chrome_binary:
                    options.binary_location = chrome_binary
            
                # Additional options to avoid detection
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Set page load strategy for faster loading
                options.page_load_strategy = 'eager'
                
                # Use system chromedriver if available (Streamlit Cloud)
                driver_path = get_chrome_driver_path()
                if driver_path:
                    service = Service(executable_path=driver_path)
                    DealScraper._driver = webdriver.Chrome(service=service, options=options)
                else:
                    DealScraper._driver = webdriver.Chrome(options=options)
                    
                # Mask webdriver property
                DealScraper._driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                
                # Set timeouts
                DealScraper._driver.set_page_load_timeout(30)
                DealScraper._driver.implicitly_wait(10)
                
                # Register cleanup on exit
                atexit.register(self._cleanup_driver)
                
                print("✅ Chrome driver initialized successfully")
                
            except Exception as e:
                print(f"❌ Failed to initialize Chrome driver: {e}")
                DealScraper._driver = None
                
        return DealScraper._driver

    @classmethod
    def _cleanup_driver(cls):
        """Clean up the Chrome driver on exit"""
        if cls._driver is not None:
            try:
                cls._driver.quit()
                print("🧹 Chrome driver cleaned up")
            except:
                pass
            finally:
                cls._driver = None

    def _make_http_call(self, url: str, wait_time: int = 3) -> Optional[str]:
        """
        Make HTTP call using Selenium to bypass anti-scraping measures
        
        Args:
            url: The URL to fetch
            wait_time: Time to wait for page to load (seconds)
            
        Returns:
            Page source HTML as string, or None if failed
        """
        # Prevent concurrent access to driver
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get or create driver
                driver = self._get_chrome_driver()
                
                if driver is None:
                    print("⚠️ Driver not available, falling back to requests")
                    return None
                
                # Navigate to URL
                driver.get(url)
                
                # Wait for page to load
                time.sleep(wait_time)
                
                # Get page source
                page_source = driver.page_source
                
                return page_source
                
            except WebDriverException as e:
                print(f"⚠️ WebDriver error (attempt {retry_count + 1}/{max_retries}): {str(e)[:100]}")
                
                # If driver is broken, reset it
                if "invalid session id" in str(e).lower() or "chrome not reachable" in str(e).lower():
                    self._cleanup_driver()
                    DealScraper._driver = None
                
                retry_count += 1
                
                if retry_count < max_retries:
                    time.sleep(2)
                else:
                    return None
                    
            except Exception as e:
                print(f"❌ Error in Selenium call to {url}: {e}")
                return None
    
    def _get_user_agent(self):
        """
        Generate appropriate user agent based on actual system
        This makes requests look more legitimate
        """
        system = platform.system()
        machine = platform.machine()
        
        # Detect Chrome version (common versions)
        chrome_versions = ['120.0.0.0', '119.0.0.0', '121.0.0.0']
        chrome_version = random.choice(chrome_versions)
        
        if system == 'Linux':
            # Ubuntu/Linux user agents
            if 'x86_64' in machine or 'AMD64' in machine:
                return f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
            else:
                return f'Mozilla/5.0 (X11; Linux {machine}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        
        elif system == 'Darwin':  # macOS
            return f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        
        elif system == 'Windows':
            return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        
        else:
            # Fallback to generic Linux
            return f'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
    
    def get_current_user_agent(self):
        """Return the current user agent being used"""
        return self.user_agent
    
    def search_amazon(self, product_name: str, max_results: int = 3) -> List[Dict]:
        """Search Amazon for products"""
        deals = []
        try:
            search_url = f"https://www.amazon.com/s?k={quote_plus(product_name)}"
            
            # Use Selenium instead of session.get
            if self.use_selenium:
                page_content = self._make_http_call(search_url)
                if not page_content:
                    print("⚠️ Failed to fetch Amazon with Selenium, trying requests...")
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code != 200:
                        return deals
                    page_content = response.content
            else:
                response = self.session.get(search_url, timeout=10)
                if response.status_code != 200:
                    return deals
                page_content = response.content
            
            soup = BeautifulSoup(page_content, 'lxml')
            
            # Find product cards
            products = soup.find_all('div', {'data-component-type': 's-search-result'}, limit=max_results)
            for product in products:
                try:
                    # Extract title
                    title_elem = product.find('h2', class_='a-size-medium a-spacing-none a-color-base a-text-normal')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract price
                    price_elem = product.find('span', class_='a-price-whole')
                    if not price_elem:
                        continue
                    price_str = price_elem.get_text(strip=True).replace(',', '').replace('$', '')
                    price = float(price_str)
                    # Extract original price (if on sale)
                    original_price_elem = product.find('span', class_='a-price a-text-price')
                    original_price_text = original_price_elem.find('span',class_='a-offscreen')
                    original_price = price
                    if original_price_text:
                        original_str = original_price_text.get_text(strip=True).replace('$', '').replace(',', '')
                        try:
                            original_price = float(original_str)
                        except:
                            pass
                    
                    # Calculate discount
                    discount_percentage = 0
                    if original_price > price:
                        discount_percentage = int(((original_price - price) / original_price) * 100)
                    
                    # Extract URL
                    
                    link_elem = product.find('a', class_='a-link-normal s-no-outline')
                    if link_elem and link_elem.get('href'):
                        href = unquote(link_elem['href'])  # Decode URL first
                        
                        # Extract ASIN (format: /dp/B0FLFD4W5R/)
                        asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                        
                        if asin_match:
                            asin = asin_match.group(1)
                            url = f"https://www.amazon.com/dp/{asin}"
                        else:
                            url = "https://www.amazon.com" + href.split('?')[0]  # Remove query params
                    else:
                        url = search_url
                    
                    # Check availability
                    availability = "In Stock"
                    if product.find(text=re.compile("Currently unavailable|Out of Stock", re.I)):
                        availability = "Out of Stock"
                    
                    # Determine deal quality
                    deal_quality = "Fair"
                    if discount_percentage >= 30:
                        deal_quality = "Excellent"
                    elif discount_percentage >= 15:
                        deal_quality = "Good"
                    
                    deals.append({
                        'retailer': 'Amazon',
                        'product_name': title[:100],  # Truncate long titles
                        'price': price,
                            'original_price': original_price,
                        'discount_percentage': discount_percentage,
                        'url': url,
                        'availability': availability,
                        'deal_quality': deal_quality
                    })
                    
                except Exception as e:
                    print(f"Error parsing Amazon product: {e}")
                    continue
            return deals
            
        except Exception as e:
            print(f"Error searching Amazon: {e}")
            return deals
    
    def search_walmart(self, product_name: str, max_results: int = 3) -> List[Dict]:
        """Search Walmart for products using Selenium"""
        deals = []
        try:
            search_url = f"https://www.walmart.com/search?q={quote_plus(product_name)}"
            
            # Use Selenium instead of session.get
            if self.use_selenium:
                page_content = self._make_http_call(search_url, wait_time=5)
                if not page_content:
                    print("⚠️ Failed to fetch Walmart with Selenium, trying requests...")
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code != 200:
                        return deals
                    page_content = response.content
            else:
                response = self.session.get(search_url, timeout=10)
                if response.status_code != 200:
                    return deals
                page_content = response.content
            
            soup = BeautifulSoup(page_content, 'lxml')
            
            # Modern Walmart uses Next.js with data in __NEXT_DATA__ script
            next_data_script = soup.find('script', id='__NEXT_DATA__')
            
            if next_data_script and next_data_script.string:
                try:
                    data = json.loads(next_data_script.string)
                    
                    # Navigate to the search results
                    # Structure: data > props > pageProps > initialData > searchResult > itemStacks
                    page_props = data.get('props', {}).get('pageProps', {})
                    initial_data = page_props.get('initialData', {})
                    search_result = initial_data.get('searchResult', {})
                    item_stacks = search_result.get('itemStacks', [])
                    
                    if item_stacks:
                        print(f"✅ Found {len(item_stacks)} Walmart items in __NEXT_DATA__")
                        
                        for item_stack in item_stacks[:max_results]:
                            parsed_deal = self._parse_walmart_next_data(item_stack)
                            if parsed_deal:
                                deals.append(parsed_deal)
                                
                except json.JSONDecodeError as e:
                    print(f"⚠️ Could not parse Walmart __NEXT_DATA__: {e}")
                except Exception as e:
                    print(f"⚠️ Error extracting Walmart data: {e}")
            
            # Fallback: Try old JSON-LD method (in case Walmart changes back)
            if not deals:
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts[:max_results]:
                    try:
                        data = json.loads(script.string)
                        
                        if isinstance(data, list):
                            for item in data:
                                if item.get('@type') == 'Product':
                                    deals.append(self._parse_walmart_product(item))
                        elif data.get('@type') == 'Product':
                            deals.append(self._parse_walmart_product(data))
                        
                        if len(deals) >= max_results:
                            break
                            
                    except:
                        continue
            
            return deals[:max_results]
            
        except Exception as e:
            print(f"Error searching Walmart: {e}")
            return deals
    
    def _parse_walmart_next_data(self, item_stack: Dict) -> Optional[Dict]:
        """Parse Walmart product data from Next.js __NEXT_DATA__ structure"""
        try:
            # The item data is typically nested in the item_stack
            item = item_stack
            
            # Try to get the main item data
            if 'item' in item:
                item = item['item']
            
            # Extract product info
            name = item.get('name', 'Unknown Product')
            
            # Price information
            price_info = item.get('priceInfo', {})
            current_price = price_info.get('currentPrice', {})
            
            price = 0
            if isinstance(current_price, dict):
                price = float(current_price.get('price', 0))
            elif isinstance(current_price, (int, float)):
                price = float(current_price)
            
            # Check for was_price (original price before discount)
            was_price_info = price_info.get('wasPrice', {})
            original_price = price
            if isinstance(was_price_info, dict):
                was_price = was_price_info.get('price', 0)
                if was_price and was_price > price:
                    original_price = float(was_price)
            
            # Calculate discount
            discount_percentage = 0
            if original_price > price and price > 0:
                discount_percentage = int(((original_price - price) / original_price) * 100)
            
            # URL - extract usItemId or canonicalUrl
            product_id = item.get('usItemId', '')
            canonical_url = item.get('canonicalUrl', '')
            
            if canonical_url:
                url = f"https://www.walmart.com{canonical_url}"
            elif product_id:
                url = f"https://www.walmart.com/ip/{product_id}"
            else:
                url = "https://www.walmart.com"
            
            # Availability
            availability = "In Stock"
            availability_status = item.get('availabilityStatusV2', {})
            if isinstance(availability_status, dict):
                display = availability_status.get('display', '').lower()
                if 'out of stock' in display or 'unavailable' in display:
                    availability = "Out of Stock"
            
            # Determine deal quality
            deal_quality = "Fair"
            if discount_percentage >= 30:
                deal_quality = "Excellent"
            elif discount_percentage >= 15:
                deal_quality = "Good"
            
            return {
                'retailer': 'Walmart',
                'product_name': name[:100],
                'price': price,
                'original_price': original_price,
                'discount_percentage': discount_percentage,
                'url': url,
                'availability': availability,
                'deal_quality': deal_quality
            }
            
        except Exception as e:
            print(f"Error parsing Walmart product from __NEXT_DATA__: {e}")
            return None
    
    def _parse_walmart_product(self, data: Dict) -> Dict:
        """Parse Walmart product data from JSON-LD"""
        try:
            name = data.get('name', 'Unknown Product')
            
            offers = data.get('offers', {})
            price = float(offers.get('price', 0))
            url = offers.get('url', 'https://www.walmart.com')
            
            availability = "In Stock"
            if offers.get('availability') == 'http://schema.org/OutOfStock':
                availability = "Out of Stock"
            
            # Walmart doesn't always show original price in JSON-LD
            original_price = price
            discount_percentage = 0
            
            deal_quality = "Fair"
            if discount_percentage >= 30:
                deal_quality = "Excellent"
            elif discount_percentage >= 15:
                deal_quality = "Good"
            
            return {
                'retailer': 'Walmart',
                'product_name': name[:100],
                'price': price,
                'original_price': original_price,
                'discount_percentage': discount_percentage,
                'url': url,
                'availability': availability,
                'deal_quality': deal_quality
            }
        except Exception as e:
            print(f"Error parsing Walmart product: {e}")
            return None
    
    def search_bestbuy(self, product_name: str, max_results: int = 3) -> List[Dict]:
        """Search Best Buy for products"""
        deals = []
        try:
            search_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={quote_plus(product_name)}"
            
            # Use Selenium instead of session.get
            if self.use_selenium:
                page_content = self._make_http_call(search_url)
                if not page_content:
                    print("⚠️ Failed to fetch Best Buy with Selenium, trying requests...")
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code != 200:
                        return deals
                    page_content = response.content
            else:
                response = self.session.get(search_url, timeout=10)
                if response.status_code != 200:
                    return deals
                page_content = response.content
            
            soup = BeautifulSoup(page_content, 'lxml')
            
            # Find product listings
            products = soup.find_all('li', class_='product-list-item product-list-item-gridView', limit=max_results)
            
            for product in products:
                try:
                    # Extract title
                    title_elem = product.find('h2', class_='product-title')
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract price
                    price_elem = product.find('span', class_="font-sans text-default text-style-body-md-400 font-500 text-6 leading-6")
                    if not price_elem:
                        continue
                    price_str = price_elem.get_text(strip=True).replace('$', '').replace(',', '')
                    price = float(price_str)
                    
                    # Extract original price
                    original_price = price
                    original_elem = product.find('span', class_="font-sans text-default text-style-body-md-400")
                    if original_elem:
                        was_price = original_elem.get_text(strip=True).replace(',', '').replace('$', '').strip()
                        if was_price:
                            try:
                                original_price = float(was_price)
                            except:
                                pass
                    
                    # Calculate discount
                    discount_percentage = 0
                    if original_price > price:
                        discount_percentage = int(((original_price - price) / original_price) * 100)
                    
                    # Extract URL
                    link_elem = product.find('div', class_='sku-block-content-title')
                    href=link_elem.find('a',class_='product-list-item-link')
                    url = "https://www.bestbuy.com" + href['href'] if href else search_url
                    
                    # Check availability
                    availability = "In Stock"
                    if product.find(text=re.compile("Sold Out|Coming Soon", re.I)):
                        availability = "Out of Stock"
                    
                    # Determine deal quality
                    deal_quality = "Fair"
                    if discount_percentage >= 30:
                        deal_quality = "Excellent"
                    elif discount_percentage >= 15:
                        deal_quality = "Good"
                    
                    deals.append({
                        'retailer': 'Best Buy',
                        'product_name': title[:100],
                        'price': price,
                        'original_price': original_price,
                        'discount_percentage': discount_percentage,
                        'url': url,
                        'availability': availability,
                        'deal_quality': deal_quality
                    })
                    
                except Exception as e:
                    print(f"Error parsing Best Buy product: {e}")
                    continue
            
            return deals
            
        except Exception as e:
            print(f"Error searching Best Buy: {e}")
            return deals
    
    def search_all_retailers(self, product_name: str, max_per_retailer: int = 2) -> List[Dict]:
        """Search all retailers and combine results"""
        all_deals = []
        
        # Search each retailer with delay to be respectful
        retailers = [
            ('Amazon', self.search_amazon),
            ('Best Buy', self.search_bestbuy)
        ]
        
        for retailer_name, search_func in retailers:
            try:
                print(f"🔍 Searching {retailer_name}...")
                deals = search_func(product_name, max_per_retailer)
                all_deals.extend([d for d in deals if d is not None])
                time.sleep(2)  # Respectful delay between retailers
            except Exception as e:
                print(f"❌ Error searching {retailer_name}: {e}")
                continue
        
        # Sort by price (lowest first)
        all_deals.sort(key=lambda x: x['price'])
        
        return all_deals

def scrape_product_deals(product_name: str, max_results: int = 6, use_selenium: bool = True) -> List[Dict]:
    """
    Main function to scrape product deals from multiple retailers
    
    Args:
        product_name: Product to search for
        max_results: Maximum number of results to return
        use_selenium: If True, use Selenium for requests (better for bypassing blocks)
        
    Returns:
        List of deal dictionaries
    """
    scraper = DealScraper(use_selenium=use_selenium)
    deals = scraper.search_all_retailers(product_name, max_per_retailer=max_results // 3 + 1)
    return deals[:max_results]

def get_scraper_info():
    """
    Get information about the scraper configuration
    Useful for debugging
    """
    scraper = DealScraper()
    
    return {
        'platform': platform.system(),
        'machine': platform.machine(),
        'user_agent': scraper.get_current_user_agent(),
        'python_version': platform.python_version(),
        'using_selenium': scraper.use_selenium
    }

if __name__ == "__main__":
    # Show scraper configuration when run directly
    print("🔍 Web Scraper Configuration (Streamlit-Optimized)")
    print("=" * 60)
    
    info = get_scraper_info()
    
    print(f"Platform: {info['platform']}")
    print(f"Machine: {info['machine']}")
    print(f"Python: {info['python_version']}")
    print(f"Using Selenium: {info['using_selenium']}")
    print()
    print("User Agent:")
    print(f"  {info['user_agent']}")
    print()
    print("=" * 60)
    print()
    print("This scraper uses a persistent Chrome driver for better performance.")
    print("The driver is reused across requests and auto-cleanup on exit.")
    print()
    print("To test scraping, run: python test_scraper.py")
