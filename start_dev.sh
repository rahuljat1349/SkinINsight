#!/bin/bash

# CutiS - Development Startup Script
# This script starts both the backend and frontend for development

echo "🚀 Starting CutiS Development Environment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install requirements
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --quiet -r requirements.txt 2>/dev/null

# Start backend in background
echo "🏗️  Starting FastAPI backend..."
source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   Health: http://localhost:8000/health"
else
    echo "❌ Backend failed to start. Check the logs."
    kill $BACKEND_PID
    exit 1
fi

# Start frontend
echo "🎨 Starting Vue frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Give frontend time to start
sleep 5

if curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo "✅ Frontend is running at http://localhost:5173"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "🎉 Development environment is ready!"
echo "================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "📸 To test the camera functionality:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Navigate to the 'Analyze' page"
echo "   3. Upload a photo with a clear, well-lit face"
echo "   4. View your personalized skin analysis results"
echo ""
echo "💡 Tips for best results:"
echo "   - Use a photo with good lighting (not too dark or bright)"
echo "   - Ensure your face is clearly visible and facing the camera"
echo "   - Avoid shadows on your face"
echo "   - Use JPG, JPEG, PNG, or WEBP format"
echo "   - Maximum file size: 10MB"
echo ""
echo "🛑 To stop the servers: press Ctrl+C"

# Wait for user to stop
wait

# Cleanup
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
