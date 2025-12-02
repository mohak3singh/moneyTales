#!/usr/bin/env bash

# Quick run script
# Make sure setup.sh has been run first!

echo "🎮 Starting MoneyTales..."
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

echo "Starting backend..."
echo "==================="
cd backend

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first!"
    exit 1
fi

# Start backend in background
python main.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to be ready
sleep 5

# Go to frontend directory
cd ..
echo "Starting frontend..."
echo "===================="
echo ""
streamlit run frontend/streamlit_app.py

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
