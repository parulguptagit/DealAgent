#!/bin/bash

echo "🦃 Thanksgiving Deal Finder - Startup Script"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "❗ IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
    echo "   Get your API key from: https://platform.openai.com/"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Check if database exists
if [ ! -f "deals.db" ]; then
    echo "🗄️  Database will be created on first run"
fi

echo ""
echo "🚀 Starting Streamlit app..."
echo "   App will open in your browser at http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop the app"
echo ""

# Start the app
streamlit run app.py
