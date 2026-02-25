"""
FILE PURPOSE:
This file sets up the database connection for the entire backend.
It creates:
- The database engine (the "connection manager" to PostgreSQL)
- The session factory (creates database sessions for each request)
- The base class for all ORM models
- The database session dependency for FastAPI endpoints

All database operations go through the engine and session created here.

THINK OF IT AS: The "plumbing" that connects the application to the PostgreSQL database.
"""

# Import tools for database connections
from sqlalchemy import create_engine  # Creates the connection to the database
from sqlalchemy.ext.declarative import declarative_base  # Base class for ORM models
from sqlalchemy.orm import sessionmaker  # Creates database sessions

from src.core.config import settings  # Load database URL from settings


# Create the database engine
# This is the "hub" that manages all connections to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,  # PostgreSQL connection string from .env
    # pool_pre_ping sends a small test query before using a connection
    # This ensures the connection is still alive (good for long-running apps)
    pool_pre_ping=True
)

# Create a session factory class
# This is called whenever we need a new database session for an API request
SessionLocal = sessionmaker(
    autocommit=False,  # Don't automatically commit changes - wait for explicit commit()
    autoflush=False,   # Don't automatically flush changes - wait for explicit flush()
    bind=engine  # Use the engine we created above
)

# Create the base class for all ORM models
# All Lead, User, etc. models will inherit from this
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session to endpoints.
    
    HOW IT WORKS:
    - FastAPI calls this function when an endpoint needs database access
    - Creates a new session
    - Passes it to the endpoint
    - Automatically closes the session when done (even if an error occurs)
    
    This is why endpoints have: db: Session = Depends(get_db)
    """
    # Create a new database session
    db = SessionLocal()
    try:
        # Give the session to the endpoint
        yield db
    finally:
        # Always close the session when done (cleanup)
        # This is important to not run out of database connections
        db.close()


def init_db():
    """
    Initialize the database (called when the backend starts).
    
    This function ensures database tables exist.
    In this project, we use Supabase (a managed PostgreSQL service),
    so migrations are handled outside the application.
    This function is a placeholder that keeps startup hooks consistent.
    """
    # For managed databases like Supabase, schema and migrations
    # are handled outside the application. This function exists
    # to keep a consistent startup hook but does not apply DDL.
    return
