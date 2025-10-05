"""
애플리케이션 설정 파일
"""

import os
from pathlib import Path

# 기본 설정
BASE_DIR = Path(__file__).parent
FURNITURE_DATA_DIR = BASE_DIR / "furniture_data"
MODEL_DIR = BASE_DIR / "models"

# API 설정
API_TITLE = "Furniture Recommendation API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered furniture detection and recommendation system"

# 모델 설정
DETECTION_MODEL_PATH = MODEL_DIR / "detection_model.pth"
SIMILARITY_MODEL_PATH = MODEL_DIR / "similarity_model"
FURNITURE_DATABASE_PATH = FURNITURE_DATA_DIR / "furniture_database.pkl"

# 객체 탐지 설정
DETECTION_CONFIDENCE_THRESHOLD = 0.7
DETECTION_TARGET_CLASSES = ['Bed', 'Dresser', 'Chair', 'Sofa', 'Lamp', 'Table']

# 유사도 검색 설정
SIMILARITY_INPUT_SIZE = (224, 224)
DEFAULT_TOP_K = 5

# 파일 업로드 설정
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

# 로깅 설정
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# CORS 설정
CORS_ORIGINS = ["*"]
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# 환경 변수에서 설정 오버라이드
if os.getenv("DETECTION_CONFIDENCE_THRESHOLD"):
    DETECTION_CONFIDENCE_THRESHOLD = float(os.getenv("DETECTION_CONFIDENCE_THRESHOLD"))

if os.getenv("DEFAULT_TOP_K"):
    DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K"))

if os.getenv("LOG_LEVEL"):
    LOG_LEVEL = os.getenv("LOG_LEVEL")
