#!/bin/bash
# Start backend, frontend, and tray icon in development mode

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
cd ../frontend && npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

# Start tray icon (Phase 5)
if [ -d "tray-icon" ] && [ -f "tray-icon/main.py" ]; then
    echo "Starting system tray icon..."
    cd ../tray-icon
    if [ -d "venv" ]; then
        source venv/bin/activate
        python3 main.py &
        TRAY_PID=$!
        echo "Tray icon PID: $TRAY_PID"
    else
        echo "Warning: tray-icon venv not found. Skipping tray icon."
        echo "Run: cd tray-icon && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        TRAY_PID=""
    fi
else
    echo "Tray icon not yet implemented (Phase 5)"
    TRAY_PID=""
fi

echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
if [ -n "$TRAY_PID" ]; then
    echo "Tray Icon PID: $TRAY_PID"
fi
echo ""
echo "Backend running on: http://localhost:$API_PORT"
echo "Frontend running on: http://localhost:$FRONTEND_PORT"
if [ -n "$TRAY_PID" ]; then
    echo "Tray icon running in system tray"
fi
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
if [ -n "$TRAY_PID" ]; then
    trap "kill $BACKEND_PID $FRONTEND_PID $TRAY_PID 2>/dev/null" EXIT
else
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
fi
wait
