# 인증 가이드

가져가구 API의 인증 시스템 및 사용 방법을 설명합니다.

## 🔐 인증 방식

### JWT (JSON Web Token)

가져가구 API는 JWT 기반 인증을 사용합니다.

#### 토큰 구성

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_123",
    "role": "user",
    "email": "user@example.com",
    "iat": 1642234567,
    "exp": 1642238167
  }
}
```

#### 토큰 타입

- **Access Token**: API 접근용 (1시간 유효)
- **Refresh Token**: 토큰 갱신용 (7일 유효)

## 👥 사용자 타입

### 일반 사용자 (Users)

가구를 구매하고 판매하는 일반 사용자

```json
{
  "id": "user_123",
  "role": "user",
  "email": "user@example.com",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

### 라이더 (Riders)

배송을 담당하는 라이더

```json
{
  "id": "rider_456",
  "role": "rider",
  "email": "rider@example.com",
  "name": "김배송",
  "phone": "010-9876-5432",
  "vehicle_type": "motorcycle",
  "license_number": "12-34-567890"
}
```

## 🔑 인증 엔드포인트

### 사용자 회원가입

```http
POST /auth/users/signup
Content-Type: application/json
```

**요청:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "홍길동",
  "phone": "010-1234-5678"
}
```

**응답:**
```json
{
  "user": {
    "id": "user_123",
    "role": "user",
    "email": "user@example.com",
    "name": "홍길동",
    "phone": "010-1234-5678",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "tokens": {
    "token_type": "Bearer",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

### 사용자 로그인

```http
POST /auth/users/login
Content-Type: application/json
```

**요청:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답:**
```json
{
  "user": {
    "id": "user_123",
    "role": "user",
    "email": "user@example.com",
    "name": "홍길동"
  },
  "tokens": {
    "token_type": "Bearer",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

### 토큰 갱신

```http
POST /auth/refresh
Content-Type: application/json
```

**요청:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**응답:**
```json
{
  "tokens": {
    "token_type": "Bearer",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

### 로그아웃

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**응답:**
```json
{
  "message": "로그아웃되었습니다."
}
```

## 🌐 소셜 로그인

### Google 로그인

```http
POST /auth/social/google
Content-Type: application/json
```

**요청:**
```json
{
  "id_token": "google_id_token_here",
  "access_token": "google_access_token_here"
}
```

### Kakao 로그인

```http
POST /auth/social/kakao
Content-Type: application/json
```

**요청:**
```json
{
  "access_token": "kakao_access_token_here"
}
```

## 🔒 API 요청 시 인증

### 헤더에 토큰 포함

```http
GET /users/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### JavaScript 예시

```javascript
// Axios 설정
const api = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 요청 인터셉터로 토큰 자동 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터로 토큰 갱신
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 갱신 시도
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: refreshToken
          });
          const { access_token } = response.data.tokens;
          localStorage.setItem('access_token', access_token);
          
          // 원래 요청 재시도
          error.config.headers.Authorization = `Bearer ${access_token}`;
          return api.request(error.config);
        } catch (refreshError) {
          // 갱신 실패 시 로그인 페이지로 리다이렉트
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

### Python 예시

```python
import requests
import jwt
from datetime import datetime, timedelta

class AuthClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/auth/users/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["tokens"]["access_token"]
            self.refresh_token = data["tokens"]["refresh_token"]
            return data
        else:
            raise Exception("로그인 실패")
    
    def get_headers(self):
        if not self.access_token:
            raise Exception("로그인이 필요합니다")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def refresh_access_token(self):
        if not self.refresh_token:
            raise Exception("리프레시 토큰이 없습니다")
        
        response = requests.post(
            f"{self.base_url}/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["tokens"]["access_token"]
            self.refresh_token = data["tokens"]["refresh_token"]
        else:
            raise Exception("토큰 갱신 실패")

# 사용 예시
client = AuthClient("http://localhost:8001")
client.login("user@example.com", "password123")

# 인증이 필요한 API 호출
response = requests.get(
    f"{client.base_url}/users/me",
    headers=client.get_headers()
)
```

## ⚠️ 보안 고려사항

### 토큰 저장

- **웹**: `localStorage` 또는 `sessionStorage` 사용
- **모바일**: Secure Storage 사용
- **서버**: 환경변수 또는 암호화된 설정 파일

### 토큰 만료 처리

```javascript
// 토큰 만료 시간 확인
function isTokenExpired(token) {
  try {
    const decoded = jwt.decode(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    return true;
  }
}

// 자동 토큰 갱신
function autoRefreshToken() {
  const token = localStorage.getItem('access_token');
  if (token && isTokenExpired(token)) {
    refreshToken();
  }
}

// 주기적으로 토큰 상태 확인
setInterval(autoRefreshToken, 60000); // 1분마다
```

### HTTPS 사용

- **프로덕션**: 반드시 HTTPS 사용
- **개발**: 로컬에서는 HTTP 허용

## 🔧 에러 처리

### 인증 관련 에러

```json
{
  "code": "UNAUTHORIZED",
  "message": "인증이 필요합니다.",
  "details": {
    "error": "TOKEN_EXPIRED",
    "expired_at": "2024-01-15T11:30:00Z"
  }
}
```

### 주요 에러 코드

- `401 UNAUTHORIZED` - 인증 실패
- `403 FORBIDDEN` - 권한 없음
- `422 VALIDATION_ERROR` - 입력 데이터 오류
- `409 CONFLICT` - 중복 계정

## 📱 모바일 인증

### React Native 예시

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';
import { GoogleSignin } from '@react-native-google-signin/google-signin';

class AuthService {
  async login(email, password) {
    try {
      const response = await fetch('http://localhost:8001/auth/users/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      
      if (response.ok) {
        await AsyncStorage.setItem('access_token', data.tokens.access_token);
        await AsyncStorage.setItem('refresh_token', data.tokens.refresh_token);
        return data;
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      throw error;
    }
  }

  async googleLogin() {
    try {
      await GoogleSignin.hasPlayServices();
      const userInfo = await GoogleSignin.signIn();
      
      const response = await fetch('http://localhost:8001/auth/social/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: userInfo.idToken,
          access_token: userInfo.accessToken,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        await AsyncStorage.setItem('access_token', data.tokens.access_token);
        await AsyncStorage.setItem('refresh_token', data.tokens.refresh_token);
        return data;
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      throw error;
    }
  }

  async getStoredToken() {
    return await AsyncStorage.getItem('access_token');
  }

  async logout() {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
    await GoogleSignin.signOut();
  }
}
```
