# 개발 환경 설정

가져가구 서버 프로젝트의 로컬 개발 환경을 구축하는 방법을 설명합니다.

## 🛠️ 사전 요구사항

### 필수 소프트웨어
- **Python**: 3.10+ (권장 3.11)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

### 선택적 소프트웨어
- **Node.js**: 18+ (프론트엔드 개발 시)
- **PostgreSQL**: 15+ (로컬 DB 사용 시)
- **Redis**: 7+ (캐싱 사용 시)

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd gajogagu/server
```

### 2. Docker로 전체 시스템 실행
```bash
cd deploy/compose
docker-compose -f docker-compose.cpu.yaml up -d
```

### 3. 서비스 확인
```bash
# 서비스 상태 확인
docker-compose -f docker-compose.cpu.yaml ps

# API 테스트
curl http://localhost:8001/health  # CRUD API
curl http://localhost:8002/health  # DL API
```

## 🔧 상세 개발 환경 설정

### 1. CRUD API 개발 환경

#### 가상환경 설정
```bash
cd services/crud-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 환경 변수 설정
```bash
# .env 파일 생성
cat > .env << EOF
DATABASE_URL=postgresql://gajogagu:password@localhost:5432/gajogagu_db
LOG_LEVEL=DEBUG
SECRET_KEY=your-secret-key-here
EOF
```

#### 로컬 실행
```bash
# 데이터베이스 마이그레이션
python -m alembic upgrade head

# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 2. DL API 개발 환경

#### 가상환경 설정
```bash
cd services/dl-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 환경 변수 설정
```bash
# .env 파일 생성
cat > .env << EOF
DATABASE_URL=postgresql://gajogagu:password@localhost:5432/gajogagu_db
DETECTION_CONFIDENCE_THRESHOLD=0.7
DEFAULT_TOP_K=5
LOG_LEVEL=DEBUG
TF_ENABLE_ONEDNN_OPTS=0
EOF
```

#### 로컬 실행
```bash
# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### 3. 데이터베이스 설정

#### PostgreSQL 로컬 설치
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# PostgreSQL 공식 사이트에서 설치
```

#### 데이터베이스 생성
```sql
-- PostgreSQL에 접속
psql -U postgres

-- 데이터베이스 및 사용자 생성
CREATE DATABASE gajogagu_db;
CREATE USER gajogagu WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE gajogagu_db TO gajogagu;
```

## 🧪 테스트 환경

### 1. 단위 테스트 실행
```bash
# CRUD API 테스트
cd services/crud-api
python -m pytest tests/ -v

# DL API 테스트
cd services/dl-api
python -m pytest tests/ -v
```

### 2. 통합 테스트
```bash
# Docker Compose로 테스트 환경 실행
cd deploy/compose
docker-compose -f docker-compose.cpu.yaml run --rm crud-tests
```

### 3. API 테스트 (Bruno)
1. Bruno IDE 설치
2. `bruno-collection/` 디렉토리를 Bruno에서 열기
3. 각 API 엔드포인트 테스트

## 🔍 디버깅

### 1. 로그 확인
```bash
# Docker 로그
docker-compose -f docker-compose.cpu.yaml logs -f crud
docker-compose -f docker-compose.cpu.yaml logs -f dl

# 로컬 개발 시 로그
# 터미널에서 직접 확인
```

### 2. 데이터베이스 디버깅
```bash
# PostgreSQL에 직접 접속
docker-compose -f docker-compose.cpu.yaml exec postgres psql -U gajogagu -d gajogagu_db

# 테이블 구조 확인
\dt
\d products
```

### 3. API 디버깅
```bash
# API 문서 확인
# CRUD API: http://localhost:8001/docs
# DL API: http://localhost:8002/docs

# cURL로 테스트
curl -X GET "http://localhost:8001/health" -H "accept: application/json"
```

## 🛠️ 개발 도구

### 1. 코드 포맷팅
```bash
# Black 설치 및 실행
pip install black
black services/crud-api/
black services/dl-api/

# isort 설치 및 실행
pip install isort
isort services/crud-api/
isort services/dl-api/
```

### 2. 린팅
```bash
# flake8 설치 및 실행
pip install flake8
flake8 services/crud-api/
flake8 services/dl-api/

# mypy 설치 및 실행 (타입 체크)
pip install mypy
mypy services/crud-api/
mypy services/dl-api/
```

### 3. IDE 설정

#### VS Code 설정
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./services/crud-api/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"]
}
```

#### PyCharm 설정
1. File → Settings → Project → Python Interpreter
2. 가상환경 경로 설정
3. Code Style → Python → Black 설정

## 🔄 개발 워크플로우

### 1. 기능 개발
```bash
# 1. 새 브랜치 생성
git checkout -b feature/new-feature

# 2. 코드 작성 및 테스트
# 3. 커밋
git add .
git commit -m "feat: add new feature"

# 4. 푸시 및 PR 생성
git push origin feature/new-feature
```

### 2. 코드 리뷰
- PR 생성 시 자동으로 테스트 실행
- 코드 리뷰 후 머지
- 머지 후 자동 배포 (CI/CD 설정 시)

### 3. 배포
```bash
# Docker 이미지 빌드
docker-compose -f docker-compose.cpu.yaml build

# 서비스 재시작
docker-compose -f docker-compose.cpu.yaml up -d
```

## 🚨 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8001
lsof -i :8002
lsof -i :5432

# 프로세스 종료
kill -9 <PID>
```

#### 2. 가상환경 문제
```bash
# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. 데이터베이스 연결 실패
```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql  # Linux
brew services list | grep postgres  # macOS

# 연결 테스트
psql -h localhost -U gajogagu -d gajogagu_db
```

#### 4. Docker 문제
```bash
# Docker 재시작
sudo systemctl restart docker  # Linux
# Docker Desktop 재시작 (macOS/Windows)

# 컨테이너 정리
docker system prune -a
```

## 📚 추가 리소스

### 문서
- [프로젝트 구조](./project-structure.md)
- [API 통합 가이드](./api-integration.md)
- [Docker 실행 가이드](./docker-guide.md)

### 외부 링크
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [Docker 공식 문서](https://docs.docker.com/)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)

## 🤝 기여 가이드

### 1. 이슈 생성
- 버그 리포트 또는 기능 요청
- 명확한 설명과 재현 단계 포함

### 2. 코드 기여
- 코딩 스타일 가이드 준수
- 테스트 코드 작성
- 문서 업데이트

### 3. 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 추가
chore: 빌드 과정 또는 보조 도구 변경
```
