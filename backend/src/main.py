"""
FILE PURPOSE:
This is the main entry point for the entire backend application. It sets up the FastAPI web server,
configures security rules (CORS), connects all the API routes, and manages what happens when
the application starts and stops.

THINK OF IT AS: The "main switch" that powers on the entire backend system and tells it how to behave.
"""

# Import tools needed to run the web server
from contextlib import asynccontextmanager  # Tool to manage startup/shutdown events
from fastapi import FastAPI  # The web server framework
from fastapi.middleware.cors import CORSMiddleware  # Security middleware for cross-origin requests

# Import our custom configuration and database setup
from src.core.config import settings  # Load environment settings from .env file
from src.db.database import init_db  # Function to initialize the database
from src.api.routes import lead_routes  # All the API endpoints for leads


# This function runs automatically when the server starts, and when it stops
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifecycle:
    - STARTUP: Runs when server starts (prepare the database)
    - SHUTDOWN: Runs when server stops (cleanup if needed)
    """
    # --- STARTUP CODE (runs first) ---
    init_db()  # Set up database connection and tables
    
    # 'yield' means: "start the server now, then come back here when stopping"
    yield
    
    # --- SHUTDOWN CODE (runs when server stops) ---
    # Any cleanup code would go here if needed


# Create the main web application (FastAPI server)
app = FastAPI(
    title=settings.PROJECT_NAME,  # Set the API name (shows in documentation)
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",  # Where API docs are located
    lifespan=lifespan  # Attach the startup/shutdown event handler
)

# Add CORS middleware: This allows the frontend to talk to the backend from a different web address
# CORS = Cross-Origin Resource Sharing (a security feature that allows controlled access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # Which websites are allowed to access this backend
    allow_credentials=True,  # Allow sending cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all header types that frontend wants to send
)

# Include all the lead API routes (add them to the main server)
# The 'prefix' means all these routes will start with "/api/v1" (e.g., /api/v1/leads/)
app.include_router(lead_routes.router, prefix=settings.API_V1_PREFIX)


# Simple endpoint that tells you the API is working
@app.get("/")
def root():
    """
    Simple welcome endpoint.
    When someone visits the root URL (e.g., http://localhost:8000/),
    this returns a friendly message with where to find documentation.
    """
    return {"message": "Doctor Lead MVP API", "docs": "/docs"}


# Simple endpoint to check if the server is running and healthy
@app.get("/health")
def health_check():
    """
    Health check endpoint.
    External services can call this to verify the backend is alive and working.
    If this endpoint responds, the server is running normally.
    """
    return {"status": "healthy"}
