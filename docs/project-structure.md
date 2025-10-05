# 프로젝트 구조

가져가구 서버 프로젝트의 전체 구조와 각 디렉토리의 역할을 설명합니다.

## 📁 전체 디렉토리 구조

```
gajogagu/server/
├── bruno-collection/          # API 테스트 컬렉션
├── deploy/                    # 배포 관련 파일
│   └── compose/              # Docker Compose 설정
├── dl-server/                # 원본 딥러닝 서버 (참고용)
├── docker/                   # Docker 설정 파일
├── docs/                     # 프로젝트 문서
├── libs/                     # 공유 라이브러리
│   └── shared/              # 공통 유틸리티
└── services/                 # 마이크로서비스
    ├── crud-api/            # 메인 API 서버
    └── dl-api/              # AI 가구 탐지/추천 API
```

## 🔍 주요 디렉토리 상세 설명

### `/services/crud-api/`
메인 API 서버로 사용자 관리, 제품 관리, 주문 처리 등의 핵심 비즈니스 로직을 담당합니다.

```
crud-api/
├── auth/                    # 인증 관련 모듈
├── database/               # 데이터베이스 설정 및 모델
├── models/                 # Pydantic 모델 정의
├── routers/                # FastAPI 라우터
├── tests/                  # 테스트 파일
├── uploads/                # 업로드된 파일 저장소
├── main.py                 # 애플리케이션 진입점
└── requirements.txt        # Python 의존성
```

**주요 기능:**
- 사용자 인증 및 관리
- 제품 CRUD 작업
- 주문 및 결제 처리
- 장바구니 및 위시리스트
- 알림 시스템

### `/services/dl-api/`
AI 기반 가구 탐지 및 추천 시스템을 제공합니다.

```
dl-api/
├── furniture_data/         # 가구 데이터베이스
├── furniture_detection.py  # 객체 탐지 모델
├── furniture_similarity.py # 유사도 검색 모델
├── database.py            # 데이터베이스 연결 설정
├── models.py              # Pydantic 모델
├── config.py              # 설정 파일
├── main.py                # 애플리케이션 진입점
└── requirements.txt       # Python 의존성
```

**주요 기능:**
- 이미지에서 가구 객체 탐지
- 유사한 스타일의 가구 추천
- 카테고리별 필터링
- PostgreSQL과의 통합

### `/deploy/compose/`
Docker Compose를 사용한 서비스 배포 설정을 포함합니다.

```
compose/
├── docker-compose.cpu.yaml    # CPU 버전 설정
├── docker-compose.gpu.yaml    # GPU 버전 설정
├── docker-compose.env         # 환경 변수
├── init-scripts/              # 데이터베이스 초기화 스크립트
└── README.md                  # 배포 가이드
```

### `/docker/`
각 서비스별 Docker 설정 파일을 포함합니다.

```
docker/
├── crud.Dockerfile    # CRUD API용 Dockerfile
└── dl.Dockerfile      # DL API용 Dockerfile
```

### `/libs/shared/`
프로젝트 전반에서 사용되는 공통 라이브러리입니다.

```
shared/
├── errors.py      # 공통 에러 클래스
├── logging.py     # 로깅 설정
└── __init__.py
```

### `/bruno-collection/`
API 테스트를 위한 Bruno 컬렉션 파일들입니다.

```
bruno-collection/
├── 01-health-check/    # 헬스 체크 테스트
├── 02-auth/           # 인증 관련 테스트
├── 03-users/          # 사용자 관리 테스트
├── 04-categories/     # 카테고리 테스트
├── 05-products/       # 제품 관리 테스트
├── 06-cart/           # 장바구니 테스트
├── 07-orders/         # 주문 테스트
├── 08-wishlist/       # 위시리스트 테스트
└── 09-ai/             # AI API 테스트
```

## 🔗 서비스 간 통합

### 데이터베이스 통합
- 두 API 모두 PostgreSQL을 공유하여 데이터 일관성 보장
- CRUD API에서 관리하는 제품 데이터를 DL API에서 활용

### API 통합
- CRUD API: 비즈니스 로직 및 데이터 관리
- DL API: AI 기반 추천 및 탐지 기능
- 공통 데이터베이스를 통한 실시간 데이터 동기화

## 🚀 확장성 고려사항

### 마이크로서비스 아키텍처
- 각 서비스는 독립적으로 배포 및 확장 가능
- 서비스 간 느슨한 결합으로 유지보수성 향상

### 데이터베이스 설계
- 정규화된 스키마로 데이터 일관성 보장
- 인덱싱을 통한 쿼리 성능 최적화

### 컨테이너화
- Docker를 통한 환경 일관성 보장
- Docker Compose를 통한 로컬 개발 환경 구축
