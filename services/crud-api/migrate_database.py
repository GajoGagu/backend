#!/usr/bin/env python3
"""
Database migration script to add kakao_open_profile field to users table.
This script will recreate the database with the new schema.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.config import engine, Base
from database.models import User, Category, Product, Order, OrderItem, WishlistItem, Notification, ActiveToken
from database.service import DatabaseService
from sqlalchemy.orm import sessionmaker

def migrate_database():
    """Migrate database by recreating tables with new schema"""
    print("Starting database migration...")
    
    # Drop all tables
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables with new schema
    print("Creating tables with new schema...")
    Base.metadata.create_all(bind=engine)
    
    # Initialize sample data
    print("Initializing sample data...")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        service = DatabaseService(db)
        service.init_sample_data()
        print("Sample data initialized successfully!")
    except Exception as e:
        print(f"Error initializing sample data: {e}")
    finally:
        db.close()
    
    print("Database migration completed successfully!")
    print("New kakao_open_profile field has been added to the users table.")

if __name__ == "__main__":
    migrate_database()
