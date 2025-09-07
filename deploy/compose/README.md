# 가져가구 서버 Docker Compose 설정

이 디렉토리는 가져가구 서버를 Docker Compose를 사용하여 PostgreSQL과 함께 실행하기 위한 설정을 포함합니다.

## 🚀 빠른 시작

### 1. 서비스 시작
```bash
# 스크립트 사용 (권장)
./start.sh

# 또는 직접 실행
docker-compose -f docker-compose.cpu.yaml up --build -d
```

### 2. 서비스 중지
```bash
# 스크립트 사용 (권장)
./stop.sh

# 또는 직접 실행
docker-compose -f docker-compose.cpu.yaml down
```

## 📋 서비스 정보

- **CRUD API**: http://localhost:8001
- **PostgreSQL**: localhost:5432
  - 데이터베이스: `gajogagu_db`
  - 사용자: `gajogagu`
  - 비밀번호: `password`

## 🔧 유용한 명령어

### 로그 확인
```bash
# 모든 서비스 로그
docker-compose -f docker-compose.cpu.yaml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.cpu.yaml logs -f crud
docker-compose -f docker-compose.cpu.yaml logs -f postgres
```

### 서비스 상태 확인
```bash
docker-compose -f docker-compose.cpu.yaml ps
```

### 데이터베이스 접속
```bash
# PostgreSQL 컨테이너에 접속
docker exec -it gajogagu_postgres psql -U gajogagu -d gajogagu_db
```

### 컨테이너 재시작
```bash
# 특정 서비스 재시작
docker-compose -f docker-compose.cpu.yaml restart crud

# 모든 서비스 재시작
docker-compose -f docker-compose.cpu.yaml restart
```

## 🗄️ 데이터 관리

### 데이터 완전 삭제
```bash
docker-compose -f docker-compose.cpu.yaml down -v
```

### 데이터 백업
```bash
# PostgreSQL 데이터 백업
docker exec gajogagu_postgres pg_dump -U gajogagu gajogagu_db > backup.sql
```

### 데이터 복원
```bash
# PostgreSQL 데이터 복원
docker exec -i gajogagu_postgres psql -U gajogagu -d gajogagu_db < backup.sql
```

## 🔍 문제 해결

### 포트 충돌
만약 8001 또는 5432 포트가 이미 사용 중이라면, `docker-compose.env` 파일에서 포트를 변경하세요.

### 데이터베이스 연결 문제
1. PostgreSQL 컨테이너가 완전히 시작될 때까지 기다리세요 (약 30초)
2. 로그를 확인하여 연결 상태를 점검하세요:
   ```bash
   docker-compose -f docker-compose.cpu.yaml logs postgres
   ```

### 이미지 빌드 문제
캐시를 무시하고 다시 빌드하려면:
```bash
docker-compose -f docker-compose.cpu.yaml build --no-cache
```

## 📁 파일 구조

- `docker-compose.cpu.yaml`: 메인 Docker Compose 설정 파일
- `docker-compose.env`: 환경 변수 설정 파일
- `start.sh`: 서비스 시작 스크립트
- `stop.sh`: 서비스 중지 스크립트
- `init-scripts/`: PostgreSQL 초기화 스크립트 (선택사항)
