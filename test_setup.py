"""
Test script for Thanksgiving Deal Finder
Run this to verify your setup is correct
"""

import os
import sys
from openai import OpenAI

def test_environment():
    """Test if environment is properly set up"""
    print("🧪 Testing Environment Setup...")
    print("-" * 50)
    
    # Test 1: Python version
    print(f"✓ Python version: {sys.version}")
    
    # Test 2: Check if .env exists
    if os.path.exists('.env'):
        print("✓ .env file found")
    else:
        print("✗ .env file not found - create one from .env.example")
        return False
    
    # Test 3: Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        print("✓ OPENAI_API_KEY is set")
    else:
        print("✗ OPENAI_API_KEY not set or invalid")
        print("  Add your API key to .env file")
        return False
    
    return True

def test_dependencies():
    """Test if all dependencies are installed"""
    print("\n🧪 Testing Dependencies...")
    print("-" * 50)
    
    required_modules = [
        'streamlit',
        'openai',
        'requests',
        'bs4',
        'pandas',
        'apscheduler',
        'sqlite3'
    ]
    
    all_installed = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} is installed")
        except ImportError:
            print(f"✗ {module} is NOT installed")
            all_installed = False
    
    return all_installed

def test_openai_api():
    """Test OpenAI API connection"""
    print("\n🧪 Testing OpenAI API Connection...")
    print("-" * 50)
    
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✓ API call successful!")
        print(f"  Response: {result}")
        
        # Check token usage
        usage = response.usage
        print(f"  Tokens used: {usage.total_tokens} (input: {usage.prompt_tokens}, output: {usage.completion_tokens})")
        
        return True
        
    except Exception as e:
        print(f"✗ API call failed: {str(e)}")
        return False

def test_database():
    """Test database creation"""
    print("\n🧪 Testing Database...")
    print("-" * 50)
    
    try:
        import sqlite3
        
        # Test database creation
        conn = sqlite3.connect(':memory:')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)''')
        c.execute("INSERT INTO test (name) VALUES ('test')")
        c.execute("SELECT * FROM test")
        
        result = c.fetchone()
        conn.close()
        
        if result:
            print("✓ Database operations working")
            return True
        else:
            print("✗ Database operations failed")
            return False
            
    except Exception as e:
        print(f"✗ Database test failed: {str(e)}")
        return False

def test_scheduler():
    """Test APScheduler"""
    print("\n🧪 Testing Scheduler...")
    print("-" * 50)
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        
        scheduler = BackgroundScheduler()
        scheduler.start()
        
        job_count = len(scheduler.get_jobs())
        print(f"✓ Scheduler started successfully")
        print(f"  Active jobs: {job_count}")
        
        scheduler.shutdown()
        return True
        
    except Exception as e:
        print(f"✗ Scheduler test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*50)
    print("🦃 Thanksgiving Deal Finder - Setup Test")
    print("="*50 + "\n")
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("OpenAI API", test_openai_api),
        ("Database", test_database),
        ("Scheduler", test_scheduler)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 50)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the app.")
        print("\nRun: streamlit run app.py")
        return True
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
