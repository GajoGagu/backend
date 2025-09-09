from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from .models import (
    User, Category, Product, Order, OrderItem, 
    WishlistItem, CartItem, Notification, ActiveToken
)
from .config import get_db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    # User operations
    def create_user(self, email: str, password: str, name: str = None, phone: str = None) -> User:
        user_id = str(uuid.uuid4())
        password_hash = pwd_context.hash(password)
        
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            phone=phone
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    # Category operations
    def get_categories(self) -> List[Category]:
        return self.db.query(Category).all()
    
    def get_category_by_id(self, category_id: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def create_category(self, name: str, parent_id: str = None) -> Category:
        category_id = str(uuid.uuid4())
        category = Category(
            id=category_id,
            name=name,
            parent_id=parent_id
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    # Product operations
    def get_products(self, skip: int = 0, limit: int = 20, category_id: str = None) -> List[Product]:
        query = self.db.query(Product)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        return query.offset(skip).limit(limit).all()
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def create_product(self, title: str, description: str, price_amount: float, 
                      category_id: str, seller_id: str, location: Dict, 
                      attributes: Dict = None, images: List = None) -> Product:
        product_id = str(uuid.uuid4())
        product = Product(
            id=product_id,
            title=title,
            description=description,
            price_amount=price_amount,
            category_id=category_id,
            seller_id=seller_id,
            location=location,
            attributes=attributes or {},
            images=images or []
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    # Wishlist operations
    def add_to_wishlist(self, user_id: str, product_id: str) -> WishlistItem:
        # Check if already in wishlist
        existing = self.db.query(WishlistItem).filter(
            and_(WishlistItem.user_id == user_id, WishlistItem.product_id == product_id)
        ).first()
        
        if existing:
            return existing
        
        wishlist_item = WishlistItem(
            id=str(uuid.uuid4()),
            user_id=user_id,
            product_id=product_id
        )
        self.db.add(wishlist_item)
        self.db.commit()
        self.db.refresh(wishlist_item)
        return wishlist_item
    
    def remove_from_wishlist(self, user_id: str, product_id: str) -> bool:
        item = self.db.query(WishlistItem).filter(
            and_(WishlistItem.user_id == user_id, WishlistItem.product_id == product_id)
        ).first()
        
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
    
    def get_user_wishlist(self, user_id: str) -> List[WishlistItem]:
        return self.db.query(WishlistItem).filter(WishlistItem.user_id == user_id).all()
    
    # Cart operations
    def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> CartItem:
        # Check if already in cart
        existing = self.db.query(CartItem).filter(
            and_(CartItem.user_id == user_id, CartItem.product_id == product_id)
        ).first()
        
        if existing:
            existing.quantity += quantity
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        cart_item = CartItem(
            id=str(uuid.uuid4()),
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        )
        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item
    
    def update_cart_item_quantity(self, user_id: str, product_id: str, quantity: int) -> Optional[CartItem]:
        item = self.db.query(CartItem).filter(
            and_(CartItem.user_id == user_id, CartItem.product_id == product_id)
        ).first()
        
        if item:
            if quantity <= 0:
                self.db.delete(item)
            else:
                item.quantity = quantity
            self.db.commit()
            if quantity > 0:
                self.db.refresh(item)
                return item
        return None
    
    def remove_from_cart(self, user_id: str, product_id: str) -> bool:
        item = self.db.query(CartItem).filter(
            and_(CartItem.user_id == user_id, CartItem.product_id == product_id)
        ).first()
        
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
    
    def get_user_cart(self, user_id: str) -> List[CartItem]:
        return self.db.query(CartItem).filter(CartItem.user_id == user_id).all()
    
    def clear_user_cart(self, user_id: str) -> bool:
        items = self.db.query(CartItem).filter(CartItem.user_id == user_id).all()
        for item in items:
            self.db.delete(item)
        self.db.commit()
        return True
    
    # Token operations
    def add_active_token(self, user_id: str, token: str, expires_at: datetime) -> ActiveToken:
        active_token = ActiveToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(active_token)
        self.db.commit()
        self.db.refresh(active_token)
        return active_token
    
    def remove_token(self, token: str) -> bool:
        active_token = self.db.query(ActiveToken).filter(ActiveToken.token == token).first()
        if active_token:
            self.db.delete(active_token)
            self.db.commit()
            return True
        return False
    
    def is_token_active(self, token: str) -> bool:
        active_token = self.db.query(ActiveToken).filter(ActiveToken.token == token).first()
        if active_token:
            # Check if token is expired
            if active_token.expires_at and active_token.expires_at < datetime.utcnow():
                self.db.delete(active_token)
                self.db.commit()
                return False
            return True
        return False
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        active_token = self.db.query(ActiveToken).filter(ActiveToken.token == token).first()
        if active_token and active_token.expires_at and active_token.expires_at > datetime.utcnow():
            return self.get_user_by_id(active_token.user_id)
        return None
    
    def get_user_from_refresh_token(self, refresh_token: str) -> Optional[User]:
        """Get user from refresh token (simplified - in production, use proper JWT validation)"""
        # For now, we'll use the same token system for both access and refresh tokens
        # In production, you'd have separate refresh token validation
        return self.get_user_from_token(refresh_token)
    
    def revoke_user_tokens(self, user_id: str) -> bool:
        """Revoke all active tokens for a user"""
        tokens = self.db.query(ActiveToken).filter(ActiveToken.user_id == user_id).all()
        for token in tokens:
            self.db.delete(token)
        self.db.commit()
        return True
    
    # Notification operations
    def create_notification(self, user_id: str, title: str, message: str, type: str = "info") -> Notification:
        """Create a new notification for a user"""
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            type=type
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_user_notifications(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Notification]:
        """Get notifications for a user with pagination"""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_unread_notification_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    def mark_notifications_as_read(self, user_id: str, notification_ids: List[str]) -> int:
        """Mark specific notifications as read"""
        updated_count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.id.in_(notification_ids)
        ).update({"is_read": True}, synchronize_session=False)
        self.db.commit()
        return updated_count
    
    def get_or_create_social_user(self, social_id: str, email: str, name: str = None, provider: str = "social") -> User:
        """Get existing user or create new user for social login"""
        # Try to find existing user by email first
        user = self.get_user_by_email(email)
        
        if user:
            return user
        
        # Create new user for social login
        # Use social_id as password (in production, use proper social user handling)
        return self.create_user(
            email=email,
            password=social_id,  # In production, handle social users differently
            name=name or email.split("@")[0]
        )
    
    # Initialize sample data
    def init_sample_data(self):
        """Initialize sample data for development"""
        # Check if data already exists
        if self.db.query(Category).first():
            return
        
        # Create sample categories
        cat1 = Category(id="cat1", name="소파", parent_id=None)
        cat2 = Category(id="cat2", name="테이블", parent_id=None)
        self.db.add(cat1)
        self.db.add(cat2)
        
        # Create sample user
        user1 = User(
            id="user1",
            email="test@example.com",
            password_hash=pwd_context.hash("password123"),
            name="테스트 사용자"
        )
        self.db.add(user1)
        
        # Create sample product
        product1 = Product(
            id="prod1",
            title="모던 소파 3인용",
            description="깔끔한 디자인의 3인용 소파입니다.",
            price_amount=450000,
            category_id="cat1",
            seller_id="user1",
            location={
                "postcode": "12345",
                "line1": "서울시 강남구",
                "line2": "테헤란로 123",
                "city": "서울",
                "region": "강남구",
                "country": "KR"
            },
            attributes={
                "material": "가죽",
                "style": "모던",
                "color": "블랙",
                "size": "3인용",
                "condition": "like_new",
                "tags": ["모던", "가죽", "3인용"]
            },
            images=[{
                "file_id": "img1",
                "url": "https://example.com/sofa1.jpg",
                "width": 800,
                "height": 600
            }],
            stock=1,
            is_featured=True,
            likes_count=15
        )
        self.db.add(product1)
        
        self.db.commit()
