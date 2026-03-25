import os
from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Engine is the connection to your database
engine = create_engine(DATABASE_URL)

# SessionLocal is what you use to actually run queries
SessionLocal = sessionmaker(bind=engine)

# Base is the parent class for all your table models
Base = declarative_base()

# This class defines your table structure
class ProfileCache(Base):
    __tablename__ = "profile_cache"

    username = Column(String, primary_key=True)  # the GitHub username
    data = Column(JSON)                           # the full API response stored as JSON
    cached_at = Column(DateTime, default=datetime.utcnow)  # when it was saved

# This creates the table in PostgreSQL if it doesn't exist yet
def init_db():
    Base.metadata.create_all(engine)