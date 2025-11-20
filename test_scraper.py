"""
Test script for the web scraper module
Run this to verify scraping works before using in the app
"""

from scraper import scrape_product_deals, get_scraper_info
import json

def test_scraper():
    print("=" * 60)
    print("🧪 Testing Web Scraper")
    print("=" * 60)
    print()
    
    # Show configuration
    print("📋 Scraper Configuration:")
    print("-" * 60)
    info = get_scraper_info()
    print(f"Platform: {info['platform']}")
    print(f"Machine: {info['machine']}")
    print(f"Python: {info['python_version']}")
    print()
    print("User Agent:")
    print(f"  {info['user_agent']}")
    print()
    print("✅ User agent automatically matched to your system!")
    print()
    
    # Test products
    test_products = [
        "laptop",
        "headphones",
        "coffee maker"
    ]
    
    for product in test_products:
        print(f"\n📦 Testing: {product}")
        print("-" * 60)
        
        try:
            deals = scrape_product_deals(product, max_results=3)
            
            if deals:
                print(f"✅ Found {len(deals)} deals:")
                print()
                
                for i, deal in enumerate(deals, 1):
                    print(f"{i}. {deal['retailer']}")
                    print(f"   Product: {deal.get('product_name', 'N/A')[:60]}")
                    print(f"   Price: ${deal['price']:.2f}")
                    if deal['discount_percentage'] > 0:
                        print(f"   Discount: {deal['discount_percentage']}% off")
                    print(f"   URL: {deal['url'][:60]}...")
                    print(f"   Status: {deal['availability']}")
                    print()
            else:
                print(f"⚠️  No deals found for {product}")
                
        except Exception as e:
            print(f"❌ Error testing {product}: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_scraper()
