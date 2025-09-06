# CRUD API 명세서

가져가구의 메인 비즈니스 로직을 담당하는 REST API입니다.

## 🔗 기본 정보

- **Base URL**: `http://localhost:8001` (로컬), `https://api.gajogagu.com` (프로덕션)
- **API 버전**: v1.0.0
- **인증**: JWT Bearer Token
- **응답 형식**: JSON

## 📋 엔드포인트 목록

### 🔐 인증 (Authentication)

#### 사용자 인증
- `POST /auth/users/signup` - 사용자 회원가입
- `POST /auth/users/login` - 사용자 로그인
- `POST /auth/users/refresh` - 토큰 갱신
- `POST /auth/users/logout` - 로그아웃

#### 라이더 인증
- `POST /auth/riders/signup` - 라이더 회원가입
- `POST /auth/riders/login` - 라이더 로그인

#### 소셜 로그인
- `POST /auth/social/google` - Google 로그인
- `POST /auth/social/kakao` - Kakao 로그인

### 👤 사용자 관리

- `GET /users/me` - 내 정보 조회
- `PUT /users/me` - 내 정보 수정
- `DELETE /users/me` - 계정 삭제
- `GET /users/me/orders` - 내 주문 내역
- `GET /users/me/wishlist` - 내 찜 목록

### 🏷️ 카테고리

- `GET /categories` - 카테고리 목록 조회
- `GET /categories/{category_id}` - 특정 카테고리 조회

### 🛋️ 상품 (Products)

- `GET /products` - 상품 목록 조회 (검색/필터)
- `GET /products/{product_id}` - 상품 상세 조회
- `POST /products` - 상품 등록
- `PUT /products/{product_id}` - 상품 수정
- `DELETE /products/{product_id}` - 상품 삭제

### ❤️ 찜 목록 (Wishlist)

- `GET /wishlist` - 찜 목록 조회
- `POST /wishlist/{product_id}` - 찜 추가
- `DELETE /wishlist/{product_id}` - 찜 제거

### 🛒 장바구니 (Cart)

- `GET /cart` - 장바구니 조회
- `POST /cart/items` - 장바구니에 상품 추가
- `PUT /cart/items/{item_id}` - 장바구니 상품 수량 변경
- `DELETE /cart/items/{item_id}` - 장바구니에서 상품 제거
- `DELETE /cart` - 장바구니 비우기

### 🚚 배송 (Shipping)

- `GET /shipping/calculate` - 배송비 계산
- `GET /shipping/options` - 배송 옵션 조회

### 💳 주문 및 결제

- `POST /checkout` - 주문 생성
- `GET /orders` - 주문 목록 조회
- `GET /orders/{order_id}` - 주문 상세 조회
- `POST /payments` - 결제 처리
- `GET /payments/{payment_id}` - 결제 상태 조회

### 🔔 알림 (Notifications)

- `GET /notifications` - 알림 목록 조회
- `PUT /notifications/{notification_id}/read` - 알림 읽음 처리
- `DELETE /notifications/{notification_id}` - 알림 삭제

### 📁 파일 업로드

- `POST /uploads/presigned-url` - 업로드용 Pre-signed URL 생성
- `POST /uploads` - 파일 업로드

### 🤖 AI 추천

- `POST /ai/style-match` - 스타일 매칭 추천
- `GET /ai/recommendations` - 개인화 추천

### 🏥 헬스체크

- `GET /health` - 서비스 상태 확인
- `GET /healthz` - Kubernetes 헬스체크

## 🔐 인증 방식

### JWT 토큰

```http
Authorization: Bearer <access_token>
```

### 토큰 갱신

```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 📊 요청/응답 예시

### 상품 목록 조회

```http
GET /products?q=의자&category_id=chairs&price_min=50000&price_max=200000&sort=price_asc&page=1&page_size=20
```

**응답:**
```json
{
  "items": [
    {
      "id": "prod_123",
      "title": "모던 의자",
      "description": "편안한 모던 스타일 의자",
      "price": {
        "currency": "KRW",
        "amount": 150000
      },
      "images": [
        {
          "file_id": "img_456",
          "url": "https://cdn.gajogagu.com/images/chair1.jpg",
          "width": 800,
          "height": 600
        }
      ],
      "category": {
        "id": "chairs",
        "name": "의자"
      },
      "seller_id": "user_789",
      "location": {
        "city": "서울",
        "region": "강남구"
      },
      "attributes": {
        "material": "나무",
        "style": "모던",
        "color": "브라운",
        "condition": "like_new"
      },
      "stock": 1,
      "is_featured": false,
      "likes_count": 15,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 150
}
```

### AI 스타일 매칭

```http
POST /ai/style-match
```

**요청:**
```json
{
  "room_image_id": "room_img_123",
  "furniture_image_ids": ["furniture_img_456"],
  "top_k": 10,
  "filters": {
    "category_id": "chairs",
    "price_max": 300000,
    "style": "모던"
  }
}
```

**응답:**
```json
{
  "matches": [
    {
      "product": {
        "id": "prod_123",
        "title": "모던 의자",
        "price": {
          "currency": "KRW",
          "amount": 150000
        }
      },
      "score": 0.95
    }
  ],
  "generated_at": "2024-01-15T10:30:00Z"
}
```

## ⚠️ 에러 처리

### 에러 응답 형식

```json
{
  "code": "BAD_REQUEST",
  "message": "유효하지 않은 파라미터입니다.",
  "details": {
    "field": "email",
    "reason": "이메일 형식이 올바르지 않습니다."
  }
}
```

### 주요 에러 코드

- `400 BAD_REQUEST` - 잘못된 요청
- `401 UNAUTHORIZED` - 인증 실패
- `403 FORBIDDEN` - 권한 없음
- `404 NOT_FOUND` - 리소스 없음
- `409 CONFLICT` - 중복 데이터
- `422 VALIDATION_ERROR` - 유효성 검사 실패
- `500 INTERNAL_SERVER_ERROR` - 서버 오류

## 🔄 페이지네이션

### 쿼리 파라미터

- `page`: 페이지 번호 (기본값: 1)
- `page_size`: 페이지 크기 (기본값: 20, 최대: 100)

### 응답 형식

```json
{
  "items": [...],
  "page": 1,
  "page_size": 20,
  "total": 150,
  "has_next": true,
  "has_prev": false
}
```

## 🔍 검색 및 필터링

### 상품 검색

- `q`: 검색어 (제목, 설명에서 검색)
- `category_id`: 카테고리 필터
- `price_min`, `price_max`: 가격 범위
- `sort`: 정렬 방식 (`recent`, `price_asc`, `price_desc`, `popular`)
- `location`: 지역 필터
- `condition`: 상품 상태 필터

## 📱 클라이언트 가이드

### 웹 애플리케이션

```javascript
// Axios 설정
const api = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// 상품 목록 조회
const products = await api.get('/products', {
  params: { q: '의자', page: 1 }
});
```

### 모바일 애플리케이션

```dart
// Flutter HTTP 클라이언트
final response = await http.get(
  Uri.parse('http://localhost:8001/products'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
);
```
