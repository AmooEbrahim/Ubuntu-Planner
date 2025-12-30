#!/bin/bash
# Start both backend and frontend in development mode

# Load environment variables from .env (properly handle inline comments)
if [ -f ".env" ]; then
    set -a
    source <(grep -v '^#' .env | sed 's/#.*//' | sed '/^$/d')
    set +a
fi

# Default ports if not set
API_PORT=${API_PORT:-9090}
FRONTEND_PORT=${FRONTEND_PORT:-5173}

echo "Starting Ubuntu Planner in development mode..."
echo ""

# Start backend
echo "Starting backend on port $API_PORT..."
cd backend && ./run-dev.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend on port $FRONTEND_PORT..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend running on: http://localhost:$API_PORT"
echo "Frontend running on: http://localhost:$FRONTEND_PORT"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
