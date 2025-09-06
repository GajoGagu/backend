# API 개요

가져가구 프로젝트는 두 개의 독립적인 FastAPI 서비스로 구성되어 있습니다.

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Frontend      │
│   (Web/App)     │    │   (Web/App)     │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          │ HTTP/REST            │ HTTP/REST
          │                      │
┌─────────▼───────┐    ┌─────────▼───────┐
│   CRUD API      │    │   DL API        │
│   (Port 8001)   │    │   (Port 8002)   │
│                 │    │                 │
│ • 인증/사용자    │    │ • AI 추론       │
│ • 상품/카테고리  │    │ • 스트리밍      │
│ • 장바구니/주문  │    │ • 모델 관리     │
│ • 결제/알림     │    │                 │
│ • AI 추천       │    │                 │
└─────────────────┘    └─────────────────┘
```

## 🔄 서비스 간 통신

### CRUD API → DL API
- AI 스타일 매칭 요청
- 이미지 분석 요청
- 비동기 추론 작업

### 공통 데이터
- 사용자 인증 정보
- 상품 이미지
- AI 추천 결과

## 📊 API 통계

### CRUD API
- **총 엔드포인트**: 25+ 개
- **주요 기능**: 8개 카테고리
- **인증 방식**: JWT Bearer Token
- **응답 형식**: JSON

### DL API
- **총 엔드포인트**: 4개
- **주요 기능**: 추론, 스트리밍, 헬스체크
- **인증 방식**: 내부 통신 (API Key)
- **응답 형식**: JSON, Stream

## 🔐 인증 시스템

### 사용자 인증
- **일반 로그인**: 이메일/비밀번호
- **소셜 로그인**: Google, Kakao
- **토큰**: JWT (Access + Refresh)

### 라이더 인증
- **별도 계정**: 라이더 전용 인증
- **권한**: 배송 관련 기능만 접근

## 📱 클라이언트 지원

### 웹 애플리케이션
- React/Vue.js 등 SPA 프레임워크
- REST API 호출
- JWT 토큰 관리

### 모바일 애플리케이션
- React Native, Flutter 등
- 푸시 알림 지원
- 오프라인 캐싱

## 🚀 배포 환경

### 로컬 개발
```bash
# CPU 버전
docker compose -f deploy/compose/docker-compose.cpu.yaml up

# GPU 버전 (CUDA)
docker compose -f deploy/compose/docker-compose.gpu.yaml up
```

### 프로덕션
- **Kubernetes**: Kustomize를 통한 배포
- **이미지**: GitHub Container Registry
- **모니터링**: 헬스체크 엔드포인트

## 📈 성능 특성

### CRUD API
- **응답 시간**: 평균 100-200ms
- **동시 사용자**: 1000+ 지원
- **데이터베이스**: PostgreSQL (예정)

### DL API
- **추론 시간**: 50-500ms (모델에 따라)
- **동시 요청**: 2개 (GPU 메모리 제한)
- **모델 로딩**: 시작 시 1회

## 🔧 개발 도구

### API 테스트
- **Bruno Collection**: `bruno-collection/` 폴더
- **Swagger UI**: `/docs` 엔드포인트
- **OpenAPI 스키마**: `api/` 폴더

### 모니터링
- **헬스체크**: `/health`, `/healthz`
- **준비 상태**: `/readyz`
- **메트릭**: Prometheus (예정)
