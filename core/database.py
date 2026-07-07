from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .config import settings

# Create engine - works with SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create tables
def create_tables():
    Base.metadata.create_all(bind=engine)