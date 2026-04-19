#!/bin/bash
# Start all Ubuntu Planner services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting Ubuntu Planner services..."

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source <(grep -v '^#' "$PROJECT_DIR/.env" | sed 's/#.*//' | sed '/^$/d')
    set +a
fi

# Start backend
echo "Starting backend..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-1717} > /tmp/ubuntu-planner-backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev > /tmp/ubuntu-planner-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

# Wait a moment for frontend to start
sleep 3

# Start tray icon
echo "Starting tray icon..."
cd "$PROJECT_DIR/tray-icon"
source venv/bin/activate
nohup python3 indicator.py > /tmp/ubuntu-planner-tray.log 2>&1 &
TRAY_PID=$!
echo "Tray icon started (PID: $TRAY_PID)"

# Save PIDs to file for stop script
echo "$BACKEND_PID" > /tmp/ubuntu-planner.pids
echo "$FRONTEND_PID" >> /tmp/ubuntu-planner.pids
echo "$TRAY_PID" >> /tmp/ubuntu-planner.pids

echo ""
echo "All services started!"
echo "  - Backend: http://localhost:${API_PORT:-1717}"
echo "  - Frontend: http://localhost:${FRONTEND_PORT:-1718}"
echo ""
echo "Logs:"
echo "  - Backend: /tmp/ubuntu-planner-backend.log"
echo "  - Frontend: /tmp/ubuntu-planner-frontend.log"
echo "  - Tray: /tmp/ubuntu-planner-tray.log"