# Ubuntu Planner - Setup Complete

Phase 0 setup has been completed! Here's what you need to do to get started:

## Quick Start

### 1. Update MySQL Password (if needed)

If your MySQL password is not "password", update the `.env` file:
```bash
nano .env
# Change DB_PASSWORD=password to your actual password
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Make Scripts Executable

```bash
chmod +x backend/run-dev.sh
chmod +x frontend/run-dev.sh
chmod +x start-dev.sh
```

### 4. Start Development Servers

**Option A: Start both services together**
```bash
./start-dev.sh
```

**Option B: Start services separately**

Terminal 1 (Backend):
```bash
cd backend
./run-dev.sh
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:9090
- **API Documentation**: http://localhost:9090/docs

## What Was Set Up

### Backend ✅
- FastAPI application with CORS configured
- SQLAlchemy models for all database tables
- Alembic migrations configured and applied
- MySQL database created with all tables:
  - projects
  - tags
  - planning
  - sessions
  - settings
  - planning_tags (junction table)
  - session_tags (junction table)
- API route stubs for:
  - Projects (`/api/projects`)
  - Tags (`/api/tags`)
  - Planning (`/api/planning`)
  - Sessions (`/api/sessions`)
- Notification service integration
- Python virtual environment with all dependencies

### Frontend ✅
- Vue 3 + Vite project structure
- Tailwind CSS configured
- Vue Router configured
- Pinia store setup
- Axios API client
- Basic home view that connects to backend
- Language files (i18n ready)

### Configuration Files ✅
- `.env` - Environment variables
- `.env.example` - Template for environment variables
- `.gitignore` - Configured for Python and Node.js
- `ubuntu-planner.service` - systemd service file

## Install as systemd Service (Optional)

To run Ubuntu Planner as a service that starts automatically:

```bash
# Copy service file to systemd user directory
mkdir -p ~/.config/systemd/user
cp ubuntu-planner.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Enable and start the service
systemctl --user enable ubuntu-planner
systemctl --user start ubuntu-planner

# Check status
systemctl --user status ubuntu-planner
```

## Verify Everything Works

1. **Check backend health**:
   ```bash
   curl http://localhost:9090/health
   # Should return: {"status":"healthy"}
   ```

2. **Check database tables**:
   ```bash
   mysql -u root -p
   USE os_services_planner;
   SHOW TABLES;
   ```

3. **Check frontend loads**:
   Open browser to http://localhost:5173
   You should see "Ubuntu Planner" homepage with backend status showing as "healthy"

## Next Steps

Phase 0 is complete! You can now:

1. **Start Phase 1**: Implement Projects and Tags features
   - See `Documents/roadmap/1/` for details

2. **Customize**: Modify the frontend styles, add components, etc.

3. **Test**: Everything should be working end-to-end

## Troubleshooting

### Backend won't start
- Check MySQL is running: `systemctl status mysql`
- Check credentials in `.env` file
- Check virtual environment: `source backend/venv/bin/activate && python --version`

### Frontend won't start
- Make sure you ran `npm install` in the frontend directory
- Check Node.js version: `node --version` (should be 18+)

### Database connection errors
- Verify MySQL password in `.env`
- Check database exists: `mysql -u root -p -e "SHOW DATABASES LIKE 'os_services_planner';"`
- Check user permissions

### CORS errors
- Backend CORS is configured for http://localhost:5173
- If frontend runs on different port, update `backend/app/main.py`

## Project Structure

```
Ubuntu-Planner/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── services/    # Business logic
│   │   ├── tasks/       # Background tasks
│   │   ├── core/        # Config and database
│   │   └── main.py      # FastAPI app
│   ├── alembic/         # Database migrations
│   ├── venv/            # Python virtual environment
│   ├── requirements.txt
│   └── run-dev.sh
├── frontend/            # Vue 3 frontend
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── views/       # Page views
│   │   ├── stores/      # Pinia stores
│   │   ├── services/    # API services
│   │   ├── lang/        # Internationalization
│   │   ├── router/      # Vue Router
│   │   └── main.js
│   ├── package.json
│   └── run-dev.sh
├── Documents/           # Project documentation
├── .env                 # Environment variables
├── .gitignore
├── start-dev.sh         # Start both services
└── ubuntu-planner.service  # systemd service

```

Enjoy building with Ubuntu Planner!
