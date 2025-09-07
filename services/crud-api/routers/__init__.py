from .health import router as health_router
from .auth import router as auth_router
from .users import router as users_router
from .categories import router as categories_router
from .products import router as products_router
from .wishlist import router as wishlist_router
from .cart import router as cart_router
from .orders import router as orders_router
from .ai import router as ai_router

__all__ = [
    "health_router", "auth_router", "users_router", "categories_router",
    "products_router", "wishlist_router", "cart_router", "orders_router", "ai_router"
]
