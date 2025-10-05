# 데이터베이스 스키마

가져가구 서버의 PostgreSQL 데이터베이스 스키마를 설명합니다.

## 🗄️ 데이터베이스 개요

- **Database**: PostgreSQL 15
- **Connection**: `postgresql://gajogagu:password@postgres:5432/gajogagu_db`
- **Encoding**: UTF-8

## 📊 테이블 구조

### 1. Users 테이블
사용자 정보를 저장합니다.

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    role VARCHAR DEFAULT 'user',
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    name VARCHAR,
    phone VARCHAR,
    address JSON,  -- 주소 정보 (JSON 형태)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**주요 필드:**
- `id`: 사용자 고유 ID
- `role`: 사용자 역할 (user, admin)
- `email`: 이메일 주소 (유니크)
- `password_hash`: 암호화된 비밀번호
- `address`: 주소 정보 (JSON)

### 2. Categories 테이블
제품 카테고리 정보를 저장합니다.

```sql
CREATE TABLE categories (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    parent_id VARCHAR REFERENCES categories(id)
);
```

**주요 필드:**
- `id`: 카테고리 고유 ID
- `name`: 카테고리 이름
- `parent_id`: 상위 카테고리 ID (계층 구조)

### 3. Products 테이블
제품 정보를 저장합니다.

```sql
CREATE TABLE products (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    price_currency VARCHAR DEFAULT 'KRW',
    price_amount FLOAT NOT NULL,
    images JSON,  -- 이미지 URL 배열
    category_id VARCHAR REFERENCES categories(id),
    seller_id VARCHAR REFERENCES users(id),
    location JSON,  -- 위치 정보
    attributes JSON,  -- 제품 속성
    stock INTEGER DEFAULT 1,
    is_featured BOOLEAN DEFAULT FALSE,
    likes_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**주요 필드:**
- `id`: 제품 고유 ID
- `title`: 제품명
- `price_amount`: 가격
- `images`: 이미지 URL 배열 (JSON)
- `category_id`: 카테고리 ID
- `seller_id`: 판매자 ID
- `stock`: 재고 수량
- `is_featured`: 추천 제품 여부

### 4. Orders 테이블
주문 정보를 저장합니다.

```sql
CREATE TABLE orders (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    status VARCHAR DEFAULT 'pending',
    total_amount FLOAT NOT NULL,
    total_currency VARCHAR DEFAULT 'KRW',
    shipping_address JSON,
    payment_method VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**주문 상태:**
- `pending`: 대기 중
- `confirmed`: 확인됨
- `shipped`: 배송 중
- `delivered`: 배송 완료
- `cancelled`: 취소됨

### 5. Order Items 테이블
주문 상품 정보를 저장합니다.

```sql
CREATE TABLE order_items (
    id VARCHAR PRIMARY KEY,
    order_id VARCHAR REFERENCES orders(id),
    product_id VARCHAR REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price FLOAT NOT NULL
);
```

### 6. Wishlist Items 테이블
위시리스트 정보를 저장합니다.

```sql
CREATE TABLE wishlist_items (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    product_id VARCHAR REFERENCES products(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 7. Cart Items 테이블
장바구니 정보를 저장합니다.

```sql
CREATE TABLE cart_items (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    product_id VARCHAR REFERENCES products(id),
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 8. Notifications 테이블
알림 정보를 저장합니다.

```sql
CREATE TABLE notifications (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 9. Active Tokens 테이블
활성 토큰 정보를 저장합니다.

```sql
CREATE TABLE active_tokens (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR REFERENCES users(id),
    token VARCHAR UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔗 테이블 관계도

```mermaid
erDiagram
    USERS ||--o{ PRODUCTS : sells
    USERS ||--o{ ORDERS : places
    USERS ||--o{ WISHLIST_ITEMS : has
    USERS ||--o{ CART_ITEMS : has
    USERS ||--o{ NOTIFICATIONS : receives
    USERS ||--o{ ACTIVE_TOKENS : has
    
    CATEGORIES ||--o{ PRODUCTS : contains
    CATEGORIES ||--o{ CATEGORIES : parent_of
    
    PRODUCTS ||--o{ ORDER_ITEMS : included_in
    PRODUCTS ||--o{ WISHLIST_ITEMS : added_to
    PRODUCTS ||--o{ CART_ITEMS : added_to
    
    ORDERS ||--o{ ORDER_ITEMS : contains
```

## 📈 인덱스 설계

### 주요 인덱스
```sql
-- 성능 최적화를 위한 인덱스
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_seller_id ON products(seller_id);
CREATE INDEX idx_products_created_at ON products(created_at);
CREATE INDEX idx_products_is_featured ON products(is_featured);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

CREATE INDEX idx_wishlist_items_user_id ON wishlist_items(user_id);
CREATE INDEX idx_cart_items_user_id ON cart_items(user_id);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
```

## 🔍 주요 쿼리 패턴

### 1. 제품 검색 (DL API에서 사용)
```sql
SELECT p.id, p.title, p.price_amount, p.images, c.name as category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.stock > 0
  AND LOWER(c.name) = LOWER('chair')
LIMIT 1000;
```

### 2. 사용자별 주문 내역
```sql
SELECT o.*, oi.quantity, oi.price, p.title
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.user_id = 'user_123'
ORDER BY o.created_at DESC;
```

### 3. 카테고리별 제품 통계
```sql
SELECT c.name, COUNT(p.id) as product_count, AVG(p.price_amount) as avg_price
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name
ORDER BY product_count DESC;
```

## 🛠️ 데이터베이스 관리

### 초기화 스크립트
`deploy/compose/init-scripts/` 디렉토리에 데이터베이스 초기화 스크립트가 있습니다.

### 마이그레이션
```bash
# Alembic을 사용한 마이그레이션
docker-compose -f docker-compose.cpu.yaml exec crud python -m alembic upgrade head
```

### 백업 및 복원
```bash
# 데이터베이스 백업
docker-compose -f docker-compose.cpu.yaml exec postgres pg_dump -U gajogagu gajogagu_db > backup.sql

# 데이터베이스 복원
docker-compose -f docker-compose.cpu.yaml exec -T postgres psql -U gajogagu gajogagu_db < backup.sql
```

## 🔒 보안 고려사항

### 데이터 암호화
- 비밀번호는 해시화되어 저장
- 민감한 개인정보는 암호화 고려

### 접근 제어
- 데이터베이스 사용자 권한 최소화
- 애플리케이션 레벨에서 접근 제어

### 백업 보안
- 백업 파일 암호화
- 안전한 저장소에 백업 보관

## 📊 성능 모니터링

### 쿼리 성능 분석
```sql
-- 느린 쿼리 확인
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 테이블 크기 모니터링
```sql
-- 테이블별 크기 확인
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🚀 확장 계획

### 향후 개선 사항
1. **파티셔닝**: 대용량 테이블 분할
2. **읽기 전용 복제본**: 읽기 성능 향상
3. **캐싱 레이어**: Redis 도입
4. **데이터 압축**: 저장 공간 최적화
5. **실시간 분석**: TimescaleDB 도입 고려
