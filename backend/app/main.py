import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings as config_settings
from app.api import projects, tags, planning, sessions, statistics, settings
from app.tasks.notification_worker import notification_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup: Start the notification background worker
    asyncio.create_task(notification_worker.start())
    yield
    # Shutdown: Stop the notification worker
    await notification_worker.stop()


app = FastAPI(
    title="Ubuntu Planner API",
    description="Project planning and execution tracking service",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{config_settings.FRONTEND_PORT}"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(projects.router)
app.include_router(tags.router)
app.include_router(planning.router)
app.include_router(sessions.router)
app.include_router(statistics.router)
app.include_router(settings.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Ubuntu Planner API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
