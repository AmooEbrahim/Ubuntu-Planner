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
    allow_origins=[f"http://localhost:{settings.FRONTEND_PORT}"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(projects.router)
app.include_router(tags.router)
app.include_router(planning.router)
app.include_router(sessions.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Ubuntu Planner API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
