#!/usr/bin/env bash

# MoneyTales Setup and Run Guide
# This script helps you get started with the project

echo "🚀 MoneyTales Setup Guide"
echo "=========================="
echo ""

# Check Python version
echo "✅ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "backend/venv" ]; then
    cd backend
    python3 -m venv venv
    echo "   Virtual environment created"
else
    echo "   Virtual environment already exists"
    cd backend
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "   Virtual environment activated"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "   Dependencies installed"
echo ""

# Go back to project root
cd ..

# Summary
echo "✅ Setup Complete!"
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "1️⃣  Start the Backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "2️⃣  In another terminal, start the Frontend:"
echo "   streamlit run frontend/streamlit_app.py"
echo ""
echo "3️⃣  Open your browser:"
echo "   • Frontend: http://localhost:8501"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "4️⃣  Start taking quizzes!"
echo "   • Select a user profile"
echo "   • Choose a topic and difficulty"
echo "   • Take the quiz!"
echo ""
