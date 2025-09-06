import uvicorn
from fastapi import FastAPI
from database import init_sample_data
from database.config import create_tables
from routers import (
    health_router, auth_router, users_router, categories_router,
    products_router, wishlist_router, cart_router, ai_router
)

app = FastAPI(
    title="가져가구 API",
    version="1.0.0",
    description="회원/라이더 분리 로그인, 소셜 로그인, 가구 조회·찜, 장바구니/결제/주문, 알림, 제품 등록, AI 유사 스타일 추천을 포함한 REST API"
)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(wishlist_router)
app.include_router(cart_router)
app.include_router(ai_router)

# Initialize database and sample data
@app.on_event("startup")
async def startup_event():
    create_tables()
    init_sample_data()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)