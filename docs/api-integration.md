# API 통합 가이드

CRUD API와 DL API 간의 통합 방법 및 데이터 흐름을 설명합니다.

## 🎯 통합 개요

가구거거 서버는 두 개의 마이크로서비스로 구성되어 있으며, PostgreSQL 데이터베이스를 공유하여 완전히 통합된 시스템을 제공합니다.

```
┌─────────────────┐    ┌─────────────────┐
│   CRUD API      │    │    DL API       │
│   (포트 8001)   │    │   (포트 8002)   │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────────┬───────────┘
                     │
            ┌────────▼────────┐
            │   PostgreSQL    │
            │   (포트 5432)   │
            └─────────────────┘
```

## 🔗 데이터베이스 통합

### 공유 테이블 구조

두 API 모두 다음 테이블들을 공유합니다:

#### Products 테이블
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
    stock INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Categories 테이블
```sql
CREATE TABLE categories (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    parent_id VARCHAR REFERENCES categories(id)
);
```

### 데이터 흐름

1. **CRUD API**: 제품 등록, 수정, 삭제
2. **PostgreSQL**: 데이터 저장 및 관리
3. **DL API**: 제품 데이터 조회하여 AI 추천 제공

## 🔄 API 간 상호작용

### 1. 제품 등록 플로우

```mermaid
sequenceDiagram
    participant Client
    participant CRUD_API
    participant PostgreSQL
    participant DL_API

    Client->>CRUD_API: POST /products (제품 등록)
    CRUD_API->>PostgreSQL: INSERT product
    PostgreSQL-->>CRUD_API: 성공 응답
    CRUD_API-->>Client: 제품 정보 반환
    
    Note over DL_API: 제품이 추천 대상에 자동 포함됨
```

### 2. AI 추천 플로우

```mermaid
sequenceDiagram
    participant Client
    participant DL_API
    participant PostgreSQL
    participant CRUD_API

    Client->>DL_API: POST /recommend (이미지 업로드)
    DL_API->>PostgreSQL: SELECT products
    PostgreSQL-->>DL_API: 제품 목록
    DL_API->>DL_API: AI 분석 및 유사도 계산
    DL_API-->>Client: 추천 제품 목록
    
    Note over Client: 추천된 제품의 상세 정보는 CRUD_API에서 조회
```

## 🛠️ 통합 구현 방법

### 1. 데이터베이스 연결 설정

#### CRUD API (services/crud-api/database/config.py)
```python
DATABASE_URL = "postgresql://gajogagu:password@postgres:5432/gajogagu_db"
```

#### DL API (services/dl-api/database.py)
```python
DATABASE_URL = "postgresql://gajogagu:password@postgres:5432/gajogagu_db"
```

### 2. 공통 모델 정의

두 API 모두 동일한 데이터베이스 스키마를 사용하므로, 데이터 일관성이 보장됩니다.

### 3. Docker Compose 통합

```yaml
# docker-compose.cpu.yaml
services:
  postgres:
    # PostgreSQL 설정
    
  crud:
    depends_on:
      postgres:
        condition: service_healthy
    
  dl:
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://gajogagu:password@postgres:5432/gajogagu_db
```

## 📊 데이터 동기화

### 실시간 동기화
- PostgreSQL을 공유하므로 데이터 변경이 즉시 반영됩니다
- CRUD API에서 제품을 등록하면 DL API에서 즉시 추천 대상에 포함됩니다

### 데이터 일관성 보장
- 트랜잭션을 통한 데이터 무결성 보장
- 외래키 제약조건으로 참조 무결성 보장

## 🔍 API 호출 예시

### 1. 제품 등록 후 AI 추천

```bash
# 1. CRUD API로 제품 등록
curl -X POST "http://localhost:8001/products" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Modern Chair",
       "description": "Comfortable office chair",
       "price_amount": 299.99,
       "category_id": "cat_chair",
       "images": ["https://example.com/chair.jpg"]
     }'

# 2. DL API로 유사한 제품 추천
curl -X POST "http://localhost:8002/recommend" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@chair_image.jpg" \
     -F "category=chair"
```

### 2. 추천 결과에서 제품 상세 정보 조회

```bash
# DL API에서 추천받은 제품 ID로 CRUD API에서 상세 정보 조회
curl "http://localhost:8001/products/prod_123"
```

## 🚨 에러 처리 및 모니터링

### 공통 에러 처리
- 두 API 모두 동일한 에러 응답 형식 사용
- 데이터베이스 연결 실패 시 적절한 에러 메시지 제공

### 헬스 체크 통합
```bash
# 전체 시스템 상태 확인
curl http://localhost:8001/health  # CRUD API
curl http://localhost:8002/health  # DL API
```

## 🔧 개발 및 디버깅

### 로그 통합
```bash
# 모든 서비스 로그 확인
docker-compose -f docker-compose.cpu.yaml logs

# 특정 서비스 로그
docker-compose -f docker-compose.cpu.yaml logs crud
docker-compose -f docker-compose.cpu.yaml logs dl
```

### 데이터베이스 직접 접근
```bash
# PostgreSQL에 직접 접근
docker-compose -f docker-compose.cpu.yaml exec postgres psql -U gajogagu -d gajogagu_db
```

## 🚀 성능 최적화

### 데이터베이스 최적화
- 인덱싱을 통한 쿼리 성능 향상
- 연결 풀링으로 동시 연결 관리
- 쿼리 최적화로 응답 시간 단축

### API 응답 최적화
- DL API에서 제품 쿼리 시 LIMIT 적용
- 필요한 필드만 조회하여 네트워크 트래픽 감소

## 🔄 확장 계획

### 향후 개선 사항
1. **API Gateway**: 두 API를 통합하는 게이트웨이 도입
2. **캐싱 레이어**: Redis를 통한 추천 결과 캐싱
3. **이벤트 기반 통합**: 제품 변경 시 DL API에 알림
4. **마이크로서비스 간 통신**: gRPC 또는 HTTP API 호출
5. **모니터링 시스템**: Prometheus + Grafana 도입

### 보안 강화
1. **API 인증**: JWT 토큰 기반 인증
2. **데이터 암호화**: 민감한 데이터 암호화
3. **접근 제어**: 역할 기반 접근 제어 (RBAC)

## 📚 관련 문서

- [프로젝트 구조](./project-structure.md)
- [Docker 실행 가이드](./docker-guide.md)
- [CRUD API 문서](./crud-api.md)
- [DL API 문서](./dl-api.md)
- [데이터베이스 스키마](./database-schema.md)
