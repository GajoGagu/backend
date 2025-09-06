# 가져가구 API 문서

가져가구 프로젝트의 API 명세서 및 개발 가이드입니다.

## 📋 목차

- [API 개요](./api-overview.md) - 전체 API 구조 및 서비스 개요
- [CRUD API](./crud-api.md) - 메인 비즈니스 로직 API
- [DL API](./dl-api.md) - 딥러닝 추론 API
- [인증 가이드](./authentication.md) - JWT 인증 및 소셜 로그인
- [에러 코드](./error-codes.md) - API 에러 코드 및 처리 방법

## 🚀 빠른 시작

### 로컬 개발 환경

```bash
# CPU 버전으로 실행
docker compose -f deploy/compose/docker-compose.cpu.yaml up --build

# GPU 버전으로 실행 (CUDA 지원)
docker compose -f deploy/compose/docker-compose.gpu.yaml up --build
```

### 서비스 포트

- **CRUD API**: http://localhost:8001
- **DL API**: http://localhost:8002

### API 문서 확인

- **CRUD API Swagger**: http://localhost:8001/docs
- **DL API Swagger**: http://localhost:8002/docs

## 📚 API 구조

### CRUD API (메인 서비스)
- **인증**: 사용자/라이더 분리 인증, 소셜 로그인
- **상품**: 가구 카탈로그, 검색, 필터링
- **장바구니**: 쇼핑카트, 배송비 계산
- **주문**: 주문 관리, 라이더 배정
- **결제**: PG 연동 (카드, 카카오페이, 네이버페이)
- **알림**: 사용자 알림 시스템
- **AI**: 스타일 매칭 추천
- **파일**: 이미지 업로드

### DL API (딥러닝 서비스)
- **추론**: 비동기 딥러닝 모델 추론
- **스트리밍**: 실시간 데이터 스트리밍
- **헬스체크**: 모델 상태 확인

## 🔧 개발 도구

### Bruno Collection
API 테스트를 위한 Bruno Collection이 `bruno-collection/` 폴더에 포함되어 있습니다.

### OpenAPI 스키마
- `api/crud.openapi.yaml` - CRUD API 스키마
- `api/dl.openapi.yaml` - DL API 스키마

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.
