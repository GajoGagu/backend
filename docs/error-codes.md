# 에러 코드 가이드

가져가구 API의 에러 코드 및 처리 방법을 설명합니다.

## 📋 에러 응답 형식

모든 API 에러는 일관된 형식으로 응답됩니다.

```json
{
  "code": "ERROR_CODE",
  "message": "사용자에게 표시할 에러 메시지",
  "details": {
    "field": "오류가 발생한 필드명",
    "reason": "상세한 오류 원인",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 🔢 HTTP 상태 코드

### 4xx 클라이언트 에러

| 코드 | 상태 | 설명 |
|------|------|------|
| 400 | BAD_REQUEST | 잘못된 요청 |
| 401 | UNAUTHORIZED | 인증 실패 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스 없음 |
| 409 | CONFLICT | 중복 데이터 |
| 422 | VALIDATION_ERROR | 유효성 검사 실패 |
| 429 | TOO_MANY_REQUESTS | 요청 한도 초과 |

### 5xx 서버 에러

| 코드 | 상태 | 설명 |
|------|------|------|
| 500 | INTERNAL_SERVER_ERROR | 서버 내부 오류 |
| 502 | BAD_GATEWAY | 게이트웨이 오류 |
| 503 | SERVICE_UNAVAILABLE | 서비스 사용 불가 |
| 504 | GATEWAY_TIMEOUT | 게이트웨이 타임아웃 |

## 🔐 인증 관련 에러

### 401 UNAUTHORIZED

#### TOKEN_MISSING
```json
{
  "code": "TOKEN_MISSING",
  "message": "인증 토큰이 필요합니다.",
  "details": {
    "error": "Authorization header가 없습니다."
  }
}
```

#### TOKEN_INVALID
```json
{
  "code": "TOKEN_INVALID",
  "message": "유효하지 않은 토큰입니다.",
  "details": {
    "error": "토큰 형식이 올바르지 않습니다."
  }
}
```

#### TOKEN_EXPIRED
```json
{
  "code": "TOKEN_EXPIRED",
  "message": "토큰이 만료되었습니다.",
  "details": {
    "expired_at": "2024-01-15T11:30:00Z",
    "current_time": "2024-01-15T12:00:00Z"
  }
}
```

#### INVALID_CREDENTIALS
```json
{
  "code": "INVALID_CREDENTIALS",
  "message": "이메일 또는 비밀번호가 올바르지 않습니다.",
  "details": {
    "field": "email",
    "attempts_remaining": 2
  }
}
```

### 403 FORBIDDEN

#### INSUFFICIENT_PERMISSIONS
```json
{
  "code": "INSUFFICIENT_PERMISSIONS",
  "message": "이 작업을 수행할 권한이 없습니다.",
  "details": {
    "required_role": "admin",
    "user_role": "user"
  }
}
```

#### ACCOUNT_SUSPENDED
```json
{
  "code": "ACCOUNT_SUSPENDED",
  "message": "계정이 일시 정지되었습니다.",
  "details": {
    "suspended_until": "2024-01-20T10:30:00Z",
    "reason": "부적절한 행위"
  }
}
```

## 📝 유효성 검사 에러

### 422 VALIDATION_ERROR

#### INVALID_EMAIL
```json
{
  "code": "INVALID_EMAIL",
  "message": "올바른 이메일 형식이 아닙니다.",
  "details": {
    "field": "email",
    "value": "invalid-email",
    "expected_format": "user@example.com"
  }
}
```

#### PASSWORD_TOO_WEAK
```json
{
  "code": "PASSWORD_TOO_WEAK",
  "message": "비밀번호는 최소 8자 이상이어야 합니다.",
  "details": {
    "field": "password",
    "min_length": 8,
    "current_length": 5
  }
}
```

#### REQUIRED_FIELD_MISSING
```json
{
  "code": "REQUIRED_FIELD_MISSING",
  "message": "필수 필드가 누락되었습니다.",
  "details": {
    "field": "title",
    "message": "상품 제목은 필수입니다."
  }
}
```

#### INVALID_PHONE_NUMBER
```json
{
  "code": "INVALID_PHONE_NUMBER",
  "message": "올바른 전화번호 형식이 아닙니다.",
  "details": {
    "field": "phone",
    "value": "123-456",
    "expected_format": "010-1234-5678"
  }
}
```

## 🔍 리소스 관련 에러

### 404 NOT_FOUND

#### USER_NOT_FOUND
```json
{
  "code": "USER_NOT_FOUND",
  "message": "사용자를 찾을 수 없습니다.",
  "details": {
    "user_id": "user_123",
    "suggestion": "사용자 ID를 확인해주세요."
  }
}
```

#### PRODUCT_NOT_FOUND
```json
{
  "code": "PRODUCT_NOT_FOUND",
  "message": "상품을 찾을 수 없습니다.",
  "details": {
    "product_id": "prod_456",
    "suggestion": "상품이 삭제되었거나 존재하지 않습니다."
  }
}
```

#### ORDER_NOT_FOUND
```json
{
  "code": "ORDER_NOT_FOUND",
  "message": "주문을 찾을 수 없습니다.",
  "details": {
    "order_id": "order_789"
  }
}
```

### 409 CONFLICT

#### EMAIL_ALREADY_EXISTS
```json
{
  "code": "EMAIL_ALREADY_EXISTS",
  "message": "이미 사용 중인 이메일입니다.",
  "details": {
    "field": "email",
    "value": "user@example.com",
    "suggestion": "다른 이메일을 사용하거나 로그인을 시도해주세요."
  }
}
```

#### PRODUCT_ALREADY_IN_CART
```json
{
  "code": "PRODUCT_ALREADY_IN_CART",
  "message": "이미 장바구니에 있는 상품입니다.",
  "details": {
    "product_id": "prod_123",
    "cart_item_id": "item_456"
  }
}
```

## 🤖 AI/ML 관련 에러

### 503 SERVICE_UNAVAILABLE

#### MODEL_NOT_READY
```json
{
  "code": "MODEL_NOT_READY",
  "message": "AI 모델이 아직 준비되지 않았습니다.",
  "details": {
    "estimated_ready_time": "2024-01-15T10:35:00Z",
    "model_status": "loading"
  }
}
```

#### INFERENCE_FAILED
```json
{
  "code": "INFERENCE_FAILED",
  "message": "AI 추론 처리에 실패했습니다.",
  "details": {
    "error": "GPU 메모리 부족",
    "retry_after": 30
  }
}
```

### 429 TOO_MANY_REQUESTS

#### RATE_LIMIT_EXCEEDED
```json
{
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "요청 한도를 초과했습니다.",
  "details": {
    "limit": 100,
    "remaining": 0,
    "reset_time": "2024-01-15T11:00:00Z"
  }
}
```

## 💳 결제 관련 에러

### 400 BAD_REQUEST

#### INVALID_PAYMENT_METHOD
```json
{
  "code": "INVALID_PAYMENT_METHOD",
  "message": "지원하지 않는 결제 방법입니다.",
  "details": {
    "payment_method": "bitcoin",
    "supported_methods": ["card", "kakao", "naver"]
  }
}
```

#### PAYMENT_AMOUNT_MISMATCH
```json
{
  "code": "PAYMENT_AMOUNT_MISMATCH",
  "message": "결제 금액이 일치하지 않습니다.",
  "details": {
    "expected_amount": 150000,
    "actual_amount": 140000
  }
}
```

### 402 PAYMENT_REQUIRED

#### PAYMENT_FAILED
```json
{
  "code": "PAYMENT_FAILED",
  "message": "결제 처리에 실패했습니다.",
  "details": {
    "error_code": "CARD_DECLINED",
    "error_message": "카드가 거절되었습니다.",
    "retry_possible": true
  }
}
```

## 📁 파일 업로드 에러

### 413 PAYLOAD_TOO_LARGE

#### FILE_TOO_LARGE
```json
{
  "code": "FILE_TOO_LARGE",
  "message": "파일 크기가 너무 큽니다.",
  "details": {
    "max_size": "10MB",
    "actual_size": "15MB",
    "file_name": "large_image.jpg"
  }
}
```

### 415 UNSUPPORTED_MEDIA_TYPE

#### UNSUPPORTED_FILE_TYPE
```json
{
  "code": "UNSUPPORTED_FILE_TYPE",
  "message": "지원하지 않는 파일 형식입니다.",
  "details": {
    "file_type": "exe",
    "supported_types": ["jpg", "png", "gif", "webp"]
  }
}
```

## 🔧 클라이언트 에러 처리

### JavaScript 예시

```javascript
class APIError extends Error {
  constructor(response) {
    super(response.message);
    this.code = response.code;
    this.details = response.details;
    this.status = response.status;
  }
}

async function handleAPIError(response) {
  if (!response.ok) {
    const errorData = await response.json();
    throw new APIError({
      ...errorData,
      status: response.status
    });
  }
  return response.json();
}

// 사용 예시
try {
  const data = await fetch('/api/products', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }).then(handleAPIError);
} catch (error) {
  if (error instanceof APIError) {
    switch (error.code) {
      case 'TOKEN_EXPIRED':
        // 토큰 갱신
        await refreshToken();
        break;
      case 'PRODUCT_NOT_FOUND':
        // 상품 없음 처리
        showMessage('상품을 찾을 수 없습니다.');
        break;
      case 'RATE_LIMIT_EXCEEDED':
        // 요청 한도 초과
        showMessage('잠시 후 다시 시도해주세요.');
        break;
      default:
        showMessage(error.message);
    }
  }
}
```

### Python 예시

```python
class APIError(Exception):
    def __init__(self, code, message, details=None, status=None):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status = status
        super().__init__(message)

def handle_api_error(response):
    if not response.ok:
        error_data = response.json()
        raise APIError(
            code=error_data.get('code'),
            message=error_data.get('message'),
            details=error_data.get('details'),
            status=response.status_code
        )
    return response.json()

# 사용 예시
try:
    response = requests.get('/api/products', headers={
        'Authorization': f'Bearer {token}'
    })
    data = handle_api_error(response)
except APIError as e:
    if e.code == 'TOKEN_EXPIRED':
        # 토큰 갱신
        refresh_token()
    elif e.code == 'PRODUCT_NOT_FOUND':
        # 상품 없음 처리
        print('상품을 찾을 수 없습니다.')
    else:
        print(f'에러: {e.message}')
```

## 📊 에러 모니터링

### 에러 로깅

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "ERROR",
  "code": "PRODUCT_NOT_FOUND",
  "message": "상품을 찾을 수 없습니다.",
  "user_id": "user_123",
  "request_id": "req_456",
  "endpoint": "/api/products/prod_789",
  "method": "GET",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.100"
}
```

### 에러 통계

- **에러율**: 전체 요청 대비 에러 비율
- **상위 에러**: 가장 많이 발생하는 에러 코드
- **에러 트렌드**: 시간별 에러 발생 추이
- **사용자별 에러**: 사용자별 에러 발생 현황
