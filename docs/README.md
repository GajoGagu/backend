# Gajogagu Server Documentation

가져가구 서버 프로젝트의 전체 문서입니다.

## 📚 문서 목록

### 🏗️ 프로젝트 구조
- [프로젝트 구조](./project-structure.md) - 전체 프로젝트 구조 및 각 디렉토리 설명

### 🐳 Docker & 배포
- [Docker 실행 가이드](./docker-guide.md) - Docker Compose를 사용한 서비스 실행 방법
- [배포 가이드](./deployment-guide.md) - 프로덕션 환경 배포 방법

### 🔌 API 문서
- [CRUD API 문서](./crud-api.md) - 메인 API 서버 엔드포인트 및 사용법
- [DL API 문서](./dl-api.md) - AI 가구 탐지/추천 API 사용법

### 🗄️ 데이터베이스
- [데이터베이스 스키마](./database-schema.md) - PostgreSQL 데이터베이스 구조

### 🚀 개발 가이드
- [개발 환경 설정](./development-setup.md) - 로컬 개발 환경 구축 방법
- [API 통합 가이드](./api-integration.md) - 두 API 서비스 간 통합 방법

## 🎯 프로젝트 개요

가져가구 서버는 다음과 같은 마이크로서비스 아키텍처로 구성되어 있습니다:

- **CRUD API** (포트 8001): 사용자 관리, 제품 관리, 주문 처리 등 핵심 비즈니스 로직
- **DL API** (포트 8002): AI 기반 가구 탐지 및 추천 시스템
- **PostgreSQL** (포트 5432): 통합 데이터베이스

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.10+
- **Database**: PostgreSQL 15
- **AI/ML**: PyTorch, TensorFlow, Detectron2, OpenCV
- **Containerization**: Docker, Docker Compose
- **Deployment**: Docker Swarm (선택사항)
