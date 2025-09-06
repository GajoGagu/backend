from typing import Dict, List
from datetime import datetime

# In-memory storage (replace with real database in production)
users_db: Dict[str, Dict] = {}
riders_db: Dict[str, Dict] = {}
products_db: Dict[str, Dict] = {}
categories_db: Dict[str, Dict] = {}
wishlist_db: Dict[str, List[str]] = {}  # user_id -> [product_ids]
cart_db: Dict[str, Dict] = {}  # user_id -> cart_data
orders_db: Dict[str, Dict] = {}
notifications_db: Dict[str, List[Dict]] = {}  # user_id -> [notifications]

# JWT simulation (use proper JWT library in production)
active_tokens: Dict[str, Dict] = {}


def init_sample_data():
    """Initialize sample data for development"""
    # Sample categories
    categories_db["cat1"] = {
        "id": "cat1",
        "name": "소파",
        "parent_id": None
    }
    categories_db["cat2"] = {
        "id": "cat2", 
        "name": "테이블",
        "parent_id": None
    }
    
    # Sample products
    products_db["prod1"] = {
        "id": "prod1",
        "title": "모던 소파 3인용",
        "description": "깔끔한 디자인의 3인용 소파입니다.",
        "price": {"currency": "KRW", "amount": 450000},
        "images": [{"file_id": "img1", "url": "https://example.com/sofa1.jpg", "width": 800, "height": 600}],
        "category": categories_db["cat1"],
        "seller_id": "user1",
        "location": {
            "postcode": "12345",
            "line1": "서울시 강남구",
            "line2": "테헤란로 123",
            "city": "서울",
            "region": "강남구",
            "country": "KR"
        },
        "attributes": {
            "material": "가죽",
            "style": "모던",
            "color": "블랙",
            "size": "3인용",
            "condition": "like_new",
            "tags": ["모던", "가죽", "3인용"]
        },
        "stock": 1,
        "is_featured": True,
        "likes_count": 15,
        "created_at": datetime.now().isoformat()
    }
