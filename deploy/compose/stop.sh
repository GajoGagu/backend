#!/bin/bash

# 가져가구 서버 중지 스크립트
echo "🛑 가져가구 서버를 중지합니다..."

# Docker Compose 파일이 있는 디렉토리로 이동
cd "$(dirname "$0")"

# 서비스 중지
docker-compose -f docker-compose.cpu.yaml down

echo "✅ 서비스가 중지되었습니다!"
echo ""
echo "💡 데이터를 완전히 삭제하려면:"
echo "  docker-compose -f docker-compose.cpu.yaml down -v"
