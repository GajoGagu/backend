from .health import router as health_router
from .auth import router as auth_router
from .users import router as users_router
from .products import router as products_router
from .wishlist import router as wishlist_router
from .orders import router as orders_router
from .ads import router as ads_router

__all__ = [
    "health_router", "auth_router", "users_router",
    "products_router", "wishlist_router", "orders_router",
    "ads_router"
]
