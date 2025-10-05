# Docker 실행 가이드

가구거거 서버를 Docker Compose를 사용하여 실행하는 방법을 설명합니다.

## 🐳 사전 요구사항

- Docker Engine 20.10+
- Docker Compose 2.0+
- 최소 4GB RAM (DL API 모델 로딩용)
- GPU 지원 (선택사항, GPU 버전 사용 시)

## 🚀 빠른 시작

### 1. CPU 버전 실행 (권장)

```bash
# 프로젝트 디렉토리로 이동
cd deploy/compose

# 서비스 빌드
docker-compose -f docker-compose.cpu.yaml build

# 서비스 실행
docker-compose -f docker-compose.cpu.yaml up -d
```

### 2. GPU 버전 실행 (GPU가 있는 경우)

```bash
# NVIDIA Docker 지원 확인
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# 서비스 빌드 및 실행
docker-compose -f docker-compose.gpu.yaml build
docker-compose -f docker-compose.gpu.yaml up -d
```

## 📊 서비스 구성

### 실행되는 서비스들

| 서비스 | 포트 | 설명 |
|--------|------|------|
| PostgreSQL | 5432 | 데이터베이스 |
| CRUD API | 8001 | 메인 API 서버 |
| DL API | 8002 | AI 가구 탐지/추천 API |

### 서비스 의존성

```
PostgreSQL (5432)
    ↓
CRUD API (8001) ←→ DL API (8002)
```

- DL API는 PostgreSQL이 준비된 후 시작됩니다
- CRUD API는 PostgreSQL이 준비된 후 시작됩니다

## 🔍 서비스 상태 확인

### 실행 중인 컨테이너 확인
```bash
docker-compose -f docker-compose.cpu.yaml ps
```

### 서비스 로그 확인
```bash
# 전체 로그
docker-compose -f docker-compose.cpu.yaml logs

# 특정 서비스 로그
docker-compose -f docker-compose.cpu.yaml logs postgres
docker-compose -f docker-compose.cpu.yaml logs crud
docker-compose -f docker-compose.cpu.yaml logs dl

# 실시간 로그 확인
docker-compose -f docker-compose.cpu.yaml logs -f dl
```

### 헬스 체크
```bash
# CRUD API 헬스 체크
curl http://localhost:8001/health

# DL API 헬스 체크
curl http://localhost:8002/health

# PostgreSQL 연결 확인
docker-compose -f docker-compose.cpu.yaml exec postgres pg_isready -U gajogagu
```

## 🛠️ 개발 환경 설정

### 환경 변수 설정
`docker-compose.env` 파일을 수정하여 환경 변수를 설정할 수 있습니다:

```env
# 데이터베이스 설정
POSTGRES_DB=gajogagu_db
POSTGRES_USER=gajogagu
POSTGRES_PASSWORD=password

# API 설정
LOG_LEVEL=INFO
DETECTION_CONFIDENCE_THRESHOLD=0.7
DEFAULT_TOP_K=5
```

### 개발 모드 실행
```bash
# 개발 모드로 실행 (코드 변경 시 자동 재시작)
docker-compose -f docker-compose.cpu.yaml up --build
```

## 🧪 테스트 실행

### CRUD API 테스트
```bash
# 테스트 컨테이너 실행
docker-compose -f docker-compose.cpu.yaml run --rm crud-tests
```

### API 테스트 (Bruno)
1. Bruno IDE 설치
2. `bruno-collection/` 디렉토리를 Bruno에서 열기
3. 각 API 엔드포인트 테스트

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002
netstat -tulpn | grep :5432

# 기존 컨테이너 정리
docker-compose -f docker-compose.cpu.yaml down
```

#### 2. 메모리 부족
```bash
# Docker 메모리 사용량 확인
docker stats

# 불필요한 컨테이너 정리
docker system prune -a
```

#### 3. DL API 모델 로딩 실패
```bash
# DL API 로그 확인
docker-compose -f docker-compose.cpu.yaml logs dl

# 컨테이너 재시작
docker-compose -f docker-compose.cpu.yaml restart dl
```

#### 4. 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
docker-compose -f docker-compose.cpu.yaml exec postgres pg_isready -U gajogagu

# 데이터베이스 재시작
docker-compose -f docker-compose.cpu.yaml restart postgres
```

### 로그 레벨 조정
```bash
# 환경 변수로 로그 레벨 설정
export LOG_LEVEL=DEBUG
docker-compose -f docker-compose.cpu.yaml up -d
```

## 🛑 서비스 중지

### 모든 서비스 중지
```bash
docker-compose -f docker-compose.cpu.yaml down
```

### 데이터까지 삭제 (주의!)
```bash
docker-compose -f docker-compose.cpu.yaml down -v
```

### 특정 서비스만 중지
```bash
docker-compose -f docker-compose.cpu.yaml stop dl
```

## 📈 성능 최적화

### 리소스 제한 설정
`docker-compose.cpu.yaml`에 리소스 제한 추가:

```yaml
services:
  dl:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### GPU 메모리 최적화
```bash
# GPU 메모리 사용량 확인
nvidia-smi

# GPU 메모리 정리
docker-compose -f docker-compose.gpu.yaml restart dl
```

## 🔄 업데이트 및 재배포

### 코드 변경 후 재배포
```bash
# 이미지 재빌드
docker-compose -f docker-compose.cpu.yaml build --no-cache

# 서비스 재시작
docker-compose -f docker-compose.cpu.yaml up -d
```

### 데이터베이스 마이그레이션
```bash
# 마이그레이션 실행
docker-compose -f docker-compose.cpu.yaml exec crud python -m alembic upgrade head
```
