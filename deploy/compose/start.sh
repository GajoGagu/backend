#!/bin/bash

# 가져가구 서버 시작 스크립트
echo "🚀 가져가구 서버를 시작합니다..."

# Docker Compose 파일이 있는 디렉토리로 이동
cd "$(dirname "$0")"

# 기존 컨테이너 정리 (선택사항)
echo "🧹 기존 컨테이너를 정리합니다..."
docker-compose -f docker-compose.cpu.yaml down

# 이미지 빌드 및 서비스 시작
echo "🔨 이미지를 빌드하고 서비스를 시작합니다..."
docker-compose -f docker-compose.cpu.yaml up --build -d

# 서비스 상태 확인
echo "📊 서비스 상태를 확인합니다..."
docker-compose -f docker-compose.cpu.yaml ps

echo "✅ 서비스가 시작되었습니다!"
echo "🌐 CRUD API: http://localhost:8001"
echo "🗄️  PostgreSQL: localhost:5432"
echo ""
echo "📋 유용한 명령어:"
echo "  - 로그 확인: docker-compose -f docker-compose.cpu.yaml logs -f"
echo "  - 서비스 중지: docker-compose -f docker-compose.cpu.yaml down"
echo "  - 상태 확인: docker-compose -f docker-compose.cpu.yaml ps"
