from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from .models import (
    User, Category, Product, Order, OrderItem, 
    WishlistItem, Notification, ActiveToken, RiderDelivery
)
from .config import get_db
from passlib.context import CryptContext

# Configure bcrypt to truncate passwords >72 bytes instead of raising ValueError
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,
)

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    # User operations
    def create_user(self, email: str, password: str, name: str, phone: str, kakao_open_profile: str, role: str = "user") -> User:
        user_id = str(uuid.uuid4())
        password_hash = pwd_context.hash(password)
        
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            phone=phone,
            kakao_open_profile=kakao_open_profile,
            role=role
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
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if user and self.verify_password(password, user.password_hash):
            return user
        return None
    
    # Category operations
    def get_categories(self) -> List[Category]:
        return self.db.query(Category).all()
    
    def get_category_by_id(self, category_id: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def create_category(self, name: str, parent_id: str = None, category_id: str = None) -> Category:
        if not category_id:
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
    def get_products(self, skip: int = 0, limit: int = 20, category_id: str = None, 
                    price_min: float = None, price_max: float = None, sort: str = "recent") -> List[Product]:
        query = self.db.query(Product)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if price_min is not None:
            query = query.filter(Product.price_amount >= price_min)
        if price_max is not None:
            query = query.filter(Product.price_amount <= price_max)
        
        # Apply sorting
        if sort == "price_asc":
            query = query.order_by(Product.price_amount.asc())
        elif sort == "price_desc":
            query = query.order_by(Product.price_amount.desc())
        elif sort == "recent":
            query = query.order_by(Product.created_at.desc())
        else:
            query = query.order_by(Product.created_at.desc())  # default
            
        return query.offset(skip).limit(limit).all()
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_with_seller(self, product_id: str) -> Optional[Product]:
        """상품과 판매자 정보를 함께 조회"""
        return self.db.query(Product).join(User, Product.seller_id == User.id).filter(Product.id == product_id).first()
    
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
    
    # Cart operations removed
    
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
            if active_token.expires_at:
                # Handle both timezone-aware and timezone-naive datetimes
                now = datetime.now(timezone.utc)
                expires_at = active_token.expires_at
                
                # If expires_at is timezone-naive, assume it's UTC
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                if expires_at < now:
                    self.db.delete(active_token)
                    self.db.commit()
                    return False
            return True
        return False
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        active_token = self.db.query(ActiveToken).filter(ActiveToken.token == token).first()
        if active_token and active_token.expires_at:
            # Handle both timezone-aware and timezone-naive datetimes
            now = datetime.now(timezone.utc)
            expires_at = active_token.expires_at
            
            # If expires_at is timezone-naive, assume it's UTC
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at > now:
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
    
    def update_user(self, user_id: str, name: str = None, phone: str = None, 
                   kakao_open_profile: str = None, address: dict = None) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        if name is not None:
            user.name = name
        if phone is not None:
            user.phone = phone
        if kakao_open_profile is not None:
            user.kakao_open_profile = kakao_open_profile
        if address is not None:
            user.address = address
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user and all related data"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Revoke all tokens first
        self.revoke_user_tokens(user_id)
        
        # Delete user (cascade will handle related data)
        self.db.delete(user)
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
    
    # Removed: social login helper (get_or_create_social_user)
    
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
    
    # Rider operations
    def get_available_orders_for_delivery(self) -> List[Order]:
        """배송 가능한 주문 목록 조회 (라이더용)"""
        return self.db.query(Order).filter(
            Order.status == "pending"  # 배송 대기 중인 주문
        ).all()
    
    def get_order_with_details(self, order_id: str) -> Optional[Order]:
        """주문과 관련된 모든 정보를 포함하여 조회"""
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def create_rider_delivery(self, order_id: str, rider_id: str, delivery_fee: float) -> RiderDelivery:
        """라이더 배송 신청 생성"""
        # 주문 정보 가져오기
        order = self.get_order_with_details(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # 구매자 정보 가져오기
        buyer = self.get_user_by_id(order.user_id)
        if not buyer:
            raise ValueError("Buyer not found")
        
        # 판매자 정보 가져오기 (첫 번째 상품의 판매자)
        if not order.items:
            raise ValueError("Order has no items")
        
        first_item = order.items[0]
        product = self.get_product_by_id(first_item.product_id)
        if not product:
            raise ValueError("Product not found")
        
        seller = self.get_user_by_id(product.seller_id)
        if not seller:
            raise ValueError("Seller not found")
        
        # 판매자와 구매자 정보를 JSON으로 저장
        seller_info = {
            "id": seller.id,
            "name": seller.name,
            "phone": seller.phone,
            "address": seller.address,
            "kakao_open_profile": seller.kakao_open_profile
        }
        
        buyer_info = {
            "id": buyer.id,
            "name": buyer.name,
            "phone": buyer.phone,
            "address": order.shipping_address,  # 배송 주소 사용
            "kakao_open_profile": buyer.kakao_open_profile
        }
        
        # 라이더 배송 신청 생성
        rider_delivery = RiderDelivery(
            id=str(uuid.uuid4()),
            order_id=order_id,
            rider_id=rider_id,
            delivery_fee=delivery_fee,
            seller_info=seller_info,
            buyer_info=buyer_info
        )
        
        self.db.add(rider_delivery)
        self.db.commit()
        self.db.refresh(rider_delivery)
        return rider_delivery
    
    def get_rider_deliveries(self, rider_id: str) -> List[RiderDelivery]:
        """라이더의 배송 신청 목록 조회"""
        return self.db.query(RiderDelivery).filter(
            RiderDelivery.rider_id == rider_id
        ).order_by(RiderDelivery.created_at.desc()).all()
    
    def get_rider_delivery_by_id(self, delivery_id: str) -> Optional[RiderDelivery]:
        """라이더 배송 신청 상세 조회"""
        return self.db.query(RiderDelivery).filter(RiderDelivery.id == delivery_id).first()
    
    def update_delivery_status(self, delivery_id: str, status: str) -> Optional[RiderDelivery]:
        """배송 상태 업데이트"""
        delivery = self.get_rider_delivery_by_id(delivery_id)
        if not delivery:
            return None
        
        delivery.status = status
        delivery.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(delivery)
        return delivery
    
    def get_order_rider_deliveries(self, order_id: str) -> List[RiderDelivery]:
        """특정 주문의 라이더 배송 신청 목록 조회"""
        return self.db.query(RiderDelivery).filter(
            RiderDelivery.order_id == order_id
        ).order_by(RiderDelivery.created_at.desc()).all()
