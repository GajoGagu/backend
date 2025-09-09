import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app
from database import users_db, riders_db, products_db, categories_db, active_tokens
from database.config import get_db
from database.service import DatabaseService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for synchronous tests."""
    # Create in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    from database.models import Base
    Base.metadata.create_all(bind=engine)
    
    # Override the get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client for asynchronous tests."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def clean_databases():
    """Clean all in-memory databases before each test."""
    users_db.clear()
    riders_db.clear()
    products_db.clear()
    categories_db.clear()
    active_tokens.clear()
    yield
    # Cleanup after test
    users_db.clear()
    riders_db.clear()
    products_db.clear()
    categories_db.clear()
    active_tokens.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
        "phone": "010-1234-5678"
    }


@pytest.fixture
def sample_rider_data():
    """Sample rider data for testing."""
    return {
        "email": "rider@example.com",
        "password": "riderpassword123",
        "name": "Test Rider",
        "phone": "010-9876-5432"
    }


@pytest.fixture
def sample_category():
    """Sample category data for testing."""
    category_id = "cat-001"
    category = {
        "id": category_id,
        "name": "가구",
        "parent_id": None
    }
    categories_db[category_id] = category
    return category


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "title": "테스트 상품",
        "description": "테스트용 상품입니다.",
        "price": {
            "currency": "KRW",
            "amount": 40000
        },
        "category_id": "cat-001",
        "location": {
            "postcode": "06292",
            "line1": "서울시 강남구 테헤란로 123",
            "line2": "101호",
            "city": "서울시",
            "region": "강남구",
            "country": "KR"
        },
        "attributes": {
            "condition": "새상품",
            "brand": "테스트브랜드"
        },
        "image_file_ids": []
    }


@pytest.fixture
def authenticated_user_token(client, sample_user_data):
    """Create an authenticated user and return access token."""
    # Sign up user
    response = client.post("/auth/users/signup", json=sample_user_data)
    assert response.status_code == 201
    return response.json()["tokens"]["access_token"]


@pytest.fixture
def authenticated_rider_token(client, sample_rider_data):
    """Create an authenticated rider and return access token."""
    # Sign up rider
    response = client.post("/auth/riders/signup", json=sample_rider_data)
    assert response.status_code == 201
    return response.json()["tokens"]["access_token"]
