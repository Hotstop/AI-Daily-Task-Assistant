"""
Database Connection
===================

Handles database connection setup.

By OkayYouGotMe
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine
# NullPool for serverless environments (Railway, Render)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

logger.info("✅ Database connection configured")


def get_db():
    """
    Get database session.
    
    Usage:
        with get_db() as db:
            # do database operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
