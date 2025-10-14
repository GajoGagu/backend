import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_sample_data
from database.config import create_tables
from routers import (
    health_router, auth_router, users_router,
    products_router, wishlist_router, orders_router
)
from routers.orders_seller import router as orders_seller_router
from routers.notifications import router as notifications_router
from routers.uploads import router as uploads_router
from routers.rider import router as rider_router
from routers.order_rider import router as order_rider_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    init_sample_data()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="가져가구 API",
    version="1.0.0",
    description="회원/라이더 분리 로그인, 가구 조회·찜, 장바구니/결제/주문, 알림, 제품 등록, AI 유사 스타일 추천을 포함한 REST API",
    lifespan=lifespan
)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(wishlist_router)
app.include_router(orders_router)
app.include_router(orders_seller_router)
app.include_router(notifications_router)
app.include_router(uploads_router)
app.include_router(rider_router)
app.include_router(order_rider_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)