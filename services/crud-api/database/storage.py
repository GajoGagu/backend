from sqlalchemy.orm import Session
from .config import get_db
from .service import DatabaseService
from .models import Base, engine

# Create tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def init_sample_data():
    """Initialize sample data for development"""
    create_tables()
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        db_service = DatabaseService(db)
        db_service.init_sample_data()
    finally:
        db.close()

# Legacy in-memory stores (kept minimal for backward compatibility if referenced)
users_db = {}
products_db = {}
categories_db = {}
wishlist_db = {}
cart_db = {}
orders_db = {}
notifications_db = {}
active_tokens = {}
