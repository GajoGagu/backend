# 가져가구 API

이 문서는 현재 코드에 구현된 실제 엔드포인트만을 간단히 나열합니다. 상세 스펙은 각 서비스의 Swagger(`/docs`)에서 확인하세요.

## CRUD API

- 헬스체크
  - GET `/health`
  - GET `/healthz`
  - GET `/readyz`

- 인증 (`/auth`)
  - POST `/auth/users/signup`
  - POST `/auth/users/login`
  - POST `/auth/riders/signup`
  - POST `/auth/riders/login`

- 사용자 (`/users`)
  - GET `/users/me`

- 카테고리 (`/categories`)
  - GET `/categories`

- 상품 (`/products`)
  - GET `/products`
  - POST `/products`
  - GET `/products/{product_id}`

- 찜 (`/wishlist`)
  - GET `/wishlist`
  - POST `/wishlist/items` (query: `product_id`)
  - DELETE `/wishlist/items` (query: `product_id`)

- 장바구니 (`/cart`)
  - GET `/cart`
  - POST `/cart/items` (query: `product_id`, `quantity`)
  - POST `/cart/clear`

- 주문 (`/orders`)
  - POST `/orders`
  - GET `/orders`
  - GET `/orders/{order_id}`
  - PUT `/orders/{order_id}/status`

- AI (`/ai`)
  - POST `/ai/style-match`

## DL API

- GET `/healthz`
- GET `/readyz`
- POST `/infer`
- GET `/stream`:

## 참고

- 각 서비스의 Swagger UI: `<BASE_URL>/docs`
- 테스트용 요청은 `bruno-collection/`에서 확인

## 새로 구현된 엔드포인트

다음 엔드포인트들이 새롭게 구현되었습니다:

### 인증 관련
- **토큰 갱신**: `POST /auth/users/refresh` - refresh token으로 새로운 access token 발급
- **로그아웃**: `POST /auth/users/logout` - access token 무효화
- **소셜 로그인**: 
  - `POST /auth/social/google` - Google OAuth 로그인
  - `POST /auth/social/kakao` - Kakao OAuth 로그인

### 카테고리
- **카테고리 단건 조회**: `GET /categories/{category_id}` - 특정 카테고리 정보 조회

### 업로드
- **Presigned URL**: `POST /uploads/presigned-url` - 파일 업로드용 presigned URL 생성
- **직접 업로드**: `POST /uploads/` - 파일 직접 업로드
- **파일 조회**: `GET /uploads/{file_id}` - 업로드된 파일 조회

### 알림
- **알림 목록**: `GET /notifications` - 사용자 알림 목록 조회 (페이지네이션)
- **읽음 처리**: `POST /notifications/mark-as-read` - 특정 알림들을 읽음으로 표시
- **미읽음 개수**: `GET /notifications/unread-count` - 미읽음 알림 개수 조회

### 구현 세부사항
- 모든 엔드포인트는 기존 인증 시스템과 통합되어 있습니다
- 소셜 로그인은 Google과 Kakao OAuth 2.0을 지원합니다
- 업로드 시스템은 로컬 파일 저장을 기본으로 하며, 프로덕션에서는 클라우드 스토리지 연동이 필요합니다
- 알림 시스템은 데이터베이스 기반으로 구현되어 있습니다
