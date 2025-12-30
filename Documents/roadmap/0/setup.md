# Phase 0: Project Setup

Initial project setup including backend, frontend, database, and development environment.

## Objectives

- Set up development environment
- Create project structure
- Initialize database with schema
- Create basic backend API framework
- Create basic frontend SPA framework
- Establish development workflow

## Prerequisites

- Python 3.10+ installed
- Node.js 18+ and npm installed
- MySQL server running

## Implementation Steps

### 1. Environment Setup

**Create .env file:**
```bash
# Database
DB_CONNECTION=MySQL
DB_HOST=localhost
DB_USERNAME=root
DB_PASSWORD=password
DB_DATABASE=os_services_planner

# Notification Service
NOTIFICATION_HOST=localhost
NOTIFICATION_PORT=52346

# Application
API_HOST=localhost
API_PORT=8000
FRONTEND_PORT=5173

# Development
DEBUG=True
```

**Create .env.example** (safe to commit):
```bash
# Copy this to .env and fill in your values
DB_CONNECTION=MySQL
DB_HOST=localhost
DB_USERNAME=root
DB_PASSWORD=your_password_here
DB_DATABASE=os_services_planner

NOTIFICATION_HOST=localhost
NOTIFICATION_PORT=52346

API_HOST=localhost
API_PORT=8000
FRONTEND_PORT=5173

DEBUG=True
```

**Create .gitignore:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
.env

# Node
node_modules/
dist/
.DS_Store

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite3

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

### 2. Backend Setup

**Create directory structure:**
```bash
mkdir -p backend/app/{api,models,services,tasks,core}
mkdir -p backend/tests
mkdir -p backend/alembic/versions
```

**Create requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
python-dotenv==1.0.0
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
```

**Create backend/app/main.py** (FastAPI app):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import projects, tags, planning, sessions

app = FastAPI(
    title="Ubuntu Planner API",
    description="Project planning and execution tracking service",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(tags.router)
app.include_router(planning.router)
app.include_router(sessions.router)

@app.get("/")
async def root():
    return {"message": "Ubuntu Planner API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Create backend/app/core/config.py** (Settings):
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DB_HOST: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str

    # Notification
    NOTIFICATION_HOST: str
    NOTIFICATION_PORT: int

    # Application
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    DEBUG: bool = False

    class Config:
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_DATABASE}"

settings = Settings()
```

**Create backend/app/core/database.py** (Database connection):
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Create Alembic configuration:**
```bash
cd backend
alembic init alembic
```

**Edit backend/alembic/env.py** to use our Base and settings:
```python
from app.core.database import Base
from app.core.config import settings
from app.models import *  # Import all models

# In run_migrations_online():
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

### 3. Database Schema

**Create initial migration:**
```bash
cd backend
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

This will create tables based on models (to be created in step 4).

### 4. Create Base Models

**Create backend/app/models/project.py:**
```python
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    color = Column(String(7), nullable=False)
    description = Column(Text, nullable=True)
    default_duration = Column(Integer, nullable=False, default=60)
    notification_interval = Column(Integer, nullable=True)
    is_archived = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    parent = relationship("Project", remote_side=[id], back_populates="children")
    children = relationship("Project", back_populates="parent")
```

**Create backend/app/models/tag.py:**
```python
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project")
```

**Create backend/app/models/planning.py, session.py, etc.**
(Follow schema in Documents/readme-database.md)

**Create backend/app/models/__init__.py:**
```python
from .project import Project
from .tag import Tag
from .planning import Planning
from .session import Session
# Import all models for Alembic auto-detection
```

### 5. Frontend Setup

**Initialize Vue project:**
```bash
npm create vue@latest frontend
# Select: Vue 3, Router, Pinia, No TypeScript (or Yes if preferred)
cd frontend
npm install
```

**Install additional dependencies:**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install axios dayjs
```

**Configure Tailwind (tailwind.config.js):**
```js
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Create frontend/src/services/api.js:**
```js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

// Add request interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
```

**Create frontend/src/lang/en.json:**
```json
{
  "common": {
    "loading": "Loading...",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit"
  },
  "errors": {
    "failed_to_load": "Failed to load data"
  }
}
```

**Create basic directory structure:**
```bash
mkdir -p frontend/src/{components,views,stores,services,lang}
```

### 6. Create systemd Service

**Create ubuntu-planner.service:**
```ini
[Unit]
Description=Ubuntu Planner Service
After=network.target mysql.service

[Service]
Type=simple
User=%u
WorkingDirectory=/home/%u/bin/bash/Ubuntu-Planner/backend
Environment="PATH=/home/%u/bin/bash/Ubuntu-Planner/backend/venv/bin"
ExecStart=/home/%u/bin/bash/Ubuntu-Planner/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

**Install service:**
```bash
mkdir -p ~/.config/systemd/user
cp ubuntu-planner.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable ubuntu-planner
systemctl --user start ubuntu-planner
```

### 7. Development Scripts

**Create backend/run-dev.sh:**
```bash
#!/bin/bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Create frontend/run-dev.sh:**
```bash
#!/bin/bash
npm run dev
```

**Create start-dev.sh in root:**
```bash
#!/bin/bash
# Start both backend and frontend in development mode
echo "Starting backend..."
cd backend && ./run-dev.sh &
BACKEND_PID=$!

echo "Starting frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

## Checklist

- [ ] Environment variables set up (.env created)
- [ ] .gitignore created
- [ ] Backend directory structure created
- [ ] requirements.txt created and dependencies installed
- [ ] FastAPI app created (main.py)
- [ ] Database connection configured
- [ ] Alembic initialized
- [ ] Database models created
- [ ] Initial migration created and applied
- [ ] Database tables created successfully
- [ ] Frontend Vue project initialized
- [ ] Tailwind CSS configured
- [ ] API service module created
- [ ] Language files created
- [ ] systemd service file created
- [ ] Development scripts created
- [ ] Backend starts successfully (http://localhost:8000)
- [ ] Frontend starts successfully (http://localhost:5173)
- [ ] API health endpoint works (GET /health)
- [ ] CORS configured correctly
- [ ] Database connection verified

## Verification Steps

### Test Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# In another terminal:
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Test Frontend
```bash
cd frontend
npm run dev

# Open browser: http://localhost:5173
# Should see Vue app running
```

### Test Database
```bash
mysql -u root -p
USE os_services_planner;
SHOW TABLES;
# Should show: projects, tags, planning, sessions, etc.
```

## Common Issues

### Issue: Database connection error
**Solution**: Check .env credentials, ensure MySQL is running

### Issue: Module not found errors
**Solution**: Ensure virtual environment activated, run `pip install -r requirements.txt`

### Issue: CORS errors in browser
**Solution**: Check CORS middleware in main.py, ensure frontend URL is allowed

### Issue: Alembic migration fails
**Solution**: Check database connection, verify models are imported in models/__init__.py

## Next Steps

After Phase 0 is complete:
- Proceed to Phase 1: Implement Projects feature
- See Documents/roadmap/1/ for next steps

## Notes

- Keep .env file secure and never commit it
- Use .env.example as template for other developers
- Run migrations before starting the app
- Use development scripts for local testing
- Use systemd service for production/daily use
