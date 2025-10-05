# DL API 문서

AI 기반 가구 탐지 및 추천 시스템 API 문서입니다.

## 🎯 개요

DL API는 이미지에서 가구 객체를 탐지하고, 유사한 스타일의 가구를 추천하는 AI 서비스를 제공합니다. PostgreSQL 데이터베이스와 통합되어 실제 제품 데이터를 기반으로 추천을 제공합니다.

## 🚀 기본 정보

- **Base URL**: `http://localhost:8002`
- **API 문서**: `http://localhost:8002/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8002/redoc`

## 🔧 기술 스택

- **Framework**: FastAPI
- **AI/ML**: PyTorch, TensorFlow, Detectron2, OpenCV
- **Database**: PostgreSQL (SQLAlchemy)
- **Image Processing**: PIL, OpenCV, NumPy

## 📡 API 엔드포인트

### 1. 헬스 체크

#### `GET /health`

서비스 상태 및 모델 로딩 상태를 확인합니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "detector_loaded": true,
  "similarity_model_loaded": true,
  "database_connected": true
}
```

### 2. 가구 객체 탐지

#### `POST /detect`

업로드된 이미지에서 가구 객체를 탐지하고 카테고리를 분류합니다.

**요청:**
- **Content-Type**: `multipart/form-data`
- **Body**: 이미지 파일 (JPEG, PNG, WebP)

**cURL 예시:**
```bash
curl -X POST "http://localhost:8002/detect" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@furniture_image.jpg"
```

**응답 예시:**
```json
{
  "success": true,
  "message": "Detected 2 furniture items",
  "detections": [
    {
      "category": "chair",
      "confidence": 0.95,
      "bbox": [100, 150, 300, 400],
      "cropped_image_path": null
    },
    {
      "category": "table",
      "confidence": 0.87,
      "bbox": [200, 300, 500, 600],
      "cropped_image_path": null
    }
  ],
  "total_count": 2
}
```

**탐지 가능한 카테고리:**
- `bed` - 침대
- `chair` - 의자
- `dresser` - 드레서
- `lamp` - 램프
- `sofa` - 소파
- `table` - 테이블

### 3. 유사한 가구 추천

#### `POST /recommend`

업로드된 가구 이미지와 유사한 스타일의 가구를 추천합니다.

**요청:**
- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `file`: 가구 이미지 파일
  - `category`: 특정 카테고리로 제한 (선택사항)
  - `top_k`: 추천할 상위 개수 (기본값: 5)

**cURL 예시:**
```bash
curl -X POST "http://localhost:8002/recommend" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@furniture_image.jpg" \
     -F "category=chair" \
     -F "top_k=5"
```

**응답 예시:**
```json
{
  "success": true,
  "message": "Found 5 similar furniture items",
  "recommendations": [
    {
      "id": "prod_123",
      "name": "Modern Office Chair",
      "category": "chair",
      "price": 299.99,
      "image_url": "https://example.com/chair123.jpg",
      "product_url": "/products/prod_123",
      "similarity_score": 0.95,
      "style_features": [0.1, 0.2, 0.3, ...]
    }
  ],
  "total_count": 5
}
```

### 4. 카테고리 목록

#### `GET /categories`

사용 가능한 가구 카테고리 목록을 반환합니다.

**응답 예시:**
```json
{
  "categories": ["bed", "chair", "dresser", "lamp", "sofa", "table"]
}
```

## 🗄️ 데이터베이스 통합

### PostgreSQL 연동

DL API는 PostgreSQL의 `products` 테이블에서 실제 제품 데이터를 조회하여 추천을 제공합니다.

**주요 테이블:**
- `products`: 제품 정보 (제목, 가격, 이미지, 카테고리)
- `categories`: 카테고리 정보

**데이터베이스 연결 설정:**
```python
DATABASE_URL = "postgresql://gajogagu:password@postgres:5432/gajogagu_db"
```

## 🤖 AI 모델 정보

### 객체 탐지 모델
- **Framework**: Detectron2
- **Model**: Faster R-CNN (COCO 사전학습)
- **Classes**: 80개 COCO 클래스 중 가구 관련 클래스 필터링
- **Input**: RGB 이미지
- **Output**: 바운딩 박스, 클래스, 신뢰도

### 유사도 검색 모델
- **Framework**: TensorFlow/Keras
- **Model**: VGG16 기반 특성 추출기
- **Input Size**: 224x224
- **Feature Dimension**: 256
- **Similarity Metric**: 코사인 유사도

## ⚙️ 설정 옵션

### 환경 변수

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `DETECTION_CONFIDENCE_THRESHOLD` | 0.7 | 객체 탐지 신뢰도 임계값 |
| `DEFAULT_TOP_K` | 5 | 기본 추천 개수 |
| `LOG_LEVEL` | INFO | 로그 레벨 |
| `TF_ENABLE_ONEDNN_OPTS` | 0 | TensorFlow 최적화 |

### 모델 설정

```python
# config.py에서 설정 가능
DETECTION_CONFIDENCE_THRESHOLD = 0.7
SIMILARITY_INPUT_SIZE = (224, 224)
DEFAULT_TOP_K = 5
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

## 🚨 에러 처리

### 일반적인 에러 코드

| 코드 | 설명 | 해결 방법 |
|------|------|-----------|
| 400 | 잘못된 요청 | 이미지 파일 형식 확인 |
| 500 | 서버 내부 오류 | 모델 로딩 상태 확인 |
| 503 | 서비스 사용 불가 | 데이터베이스 연결 확인 |

### 에러 응답 예시

```json
{
  "detail": "File must be an image"
}
```

## 🔍 성능 최적화

### 모델 로딩 최적화
- 모델은 애플리케이션 시작 시 한 번만 로드
- GPU 사용 시 CUDA 메모리 최적화
- CPU 모드 fallback 지원

### 데이터베이스 최적화
- 제품 쿼리 시 LIMIT 적용 (1000개)
- 인덱싱을 통한 카테고리 필터링 최적화
- 연결 풀링을 통한 성능 향상

## 🧪 테스트

### API 테스트 (Bruno)
`bruno-collection/09-ai/` 디렉토리에서 AI API 테스트를 수행할 수 있습니다.

### 단위 테스트
```bash
# DL API 테스트 실행
cd services/dl-api
python -m pytest tests/
```

## 🔄 모니터링

### 로그 모니터링
```bash
# DL API 로그 확인
docker-compose -f docker-compose.cpu.yaml logs -f dl
```

### 메트릭 수집
- 모델 추론 시간
- 데이터베이스 쿼리 시간
- 메모리 사용량
- GPU 사용률 (GPU 버전)

## 🚀 확장 계획

### 향후 개선 사항
1. **실제 이미지 특성 벡터 비교**: 현재 더미 유사도 점수를 실제 이미지 분석으로 교체
2. **모델 최적화**: 더 가벼운 모델로 교체하여 성능 향상
3. **캐싱 시스템**: Redis를 통한 추천 결과 캐싱
4. **배치 처리**: 여러 이미지 동시 처리 지원
5. **A/B 테스트**: 다양한 추천 알고리즘 비교
