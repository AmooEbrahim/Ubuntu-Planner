#!/bin/bash
# Stop all Ubuntu Planner services

echo "Stopping Ubuntu Planner services..."

# Read PIDs from file
if [ -f /tmp/ubuntu-planner.pids ]; then
    while read pid; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            echo "Stopped process $pid"
        fi
    done < /tmp/ubuntu-planner.pids
    rm -f /tmp/ubuntu-planner.pids
fi

# Also kill any remaining processes by name
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "Stopped backend"
pkill -f "vite" 2>/dev/null && echo "Stopped frontend"
pkill -f "indicator.py" 2>/dev/null && echo "Stopped tray"

echo "All services stopped!"