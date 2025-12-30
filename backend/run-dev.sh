#!/bin/bash
# Development script for backend

cd "$(dirname "$0")"

# Load environment variables from .env (properly handle inline comments)
if [ -f "../.env" ]; then
    set -a
    source <(grep -v '^#' ../.env | sed 's/#.*//' | sed '/^$/d')
    set +a
fi

# Default port if not set
API_PORT=${API_PORT:-9090}

source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port $API_PORT
