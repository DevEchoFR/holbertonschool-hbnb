#!/bin/bash

# HBnB Part4 - Run Backend and Frontend Together
# Usage: bash run_all.sh

cd /workspaces/holbertonschool-hbnb/part4

echo "=========================================="
echo "🚀 HBnB - Running Backend & Frontend"
echo "=========================================="
echo ""
echo "Starting Backend Server..."
echo "  Location: part4/HBnB"
echo "  Port: 5000"
echo "  URL: http://localhost:5000"
echo ""
echo "Starting Frontend Server..."
echo "  Location: part4/Frontend"
echo "  Port: 5001"
echo "  URL: http://localhost:5001"
echo ""
echo "=========================================="
echo ""

# Start backend in background
cd HBnB
python run.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 2

# Start frontend in background
cd ../Frontend
python app.py &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "=========================================="
echo "Both servers are running!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:5001"
echo "Backend API: http://localhost:5000/api/v1"
echo "Swagger Docs: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=========================================="

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
