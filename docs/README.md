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
- GET `/stream`

## 참고

- 각 서비스의 Swagger UI: `<BASE_URL>/docs`
- 테스트용 요청은 `bruno-collection/`에서 확인

## 주의 (미구현 엔드포인트)

다음 항목들은 과거 문서에 언급되었으나, 현재 코드 기준으로는 구현되어 있지 않습니다.

- 소셜 로그인: `POST /auth/social/google`, `POST /auth/social/kakao`
- 토큰 관련: `POST /auth/users/refresh`, `POST /auth/users/logout`
- 카테고리 단건 조회: `GET /categories/{category_id}`
- 결제: `POST /payments`, `GET /payments/{payment_id}`
- 업로드: `POST /uploads/presigned-url`, `POST /uploads`
- 기타: 배송 계산/옵션, 알림 목록/읽음 처리 등

필요 시 우선순위를 정해 구현 후 본 문서를 갱신하세요.
