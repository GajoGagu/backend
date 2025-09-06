# DL API 명세서

가져가구의 딥러닝 추론을 담당하는 API입니다. AI 모델을 통한 이미지 분석 및 스타일 매칭을 제공합니다.

## 🔗 기본 정보

- **Base URL**: `http://localhost:8002` (로컬), `https://dl.gajogagu.com` (프로덕션)
- **API 버전**: v1.0.0
- **인증**: API Key (내부 통신용)
- **응답 형식**: JSON, Stream

## 📋 엔드포인트 목록

### 🤖 추론 (Inference)

#### 기본 추론
- `POST /infer` - 텍스트 기반 추론
- `POST /infer/image` - 이미지 기반 추론
- `POST /infer/batch` - 배치 추론

#### 스트리밍
- `GET /stream` - 실시간 데이터 스트리밍
- `POST /stream/infer` - 스트리밍 추론

### 🏥 헬스체크

- `GET /healthz` - 서비스 상태 확인
- `GET /readyz` - 모델 준비 상태 확인

## 🔧 모델 관리

### 모델 상태

```json
{
  "model_ready": true,
  "model_version": "v1.2.0",
  "gpu_available": true,
  "concurrent_requests": 2,
  "queue_size": 0
}
```

### 모델 로딩

- **시작 시**: 서비스 시작과 함께 모델 자동 로딩
- **로딩 시간**: 약 10-30초 (모델 크기에 따라)
- **메모리 사용량**: GPU VRAM 4-8GB

## 📊 요청/응답 예시

### 기본 추론

```http
POST /infer
Content-Type: application/json
```

**요청:**
```json
{
  "text": "모던한 거실에 어울리는 의자"
}
```

**응답:**
```json
{
  "score": 0.85,
  "confidence": 0.92,
  "processing_time": 0.15,
  "model_version": "v1.2.0"
}
```

### 이미지 추론

```http
POST /infer/image
Content-Type: application/json
```

**요청:**
```json
{
  "image_url": "https://cdn.gajogagu.com/room_images/room_123.jpg",
  "task": "style_analysis",
  "options": {
    "extract_features": true,
    "return_embeddings": false
  }
}
```

**응답:**
```json
{
  "style": "modern",
  "colors": ["#2C3E50", "#ECF0F1", "#E74C3C"],
  "features": {
    "brightness": 0.7,
    "contrast": 0.6,
    "saturation": 0.5
  },
  "confidence": 0.88,
  "processing_time": 0.25
}
```

### 배치 추론

```http
POST /infer/batch
Content-Type: application/json
```

**요청:**
```json
{
  "items": [
    {
      "id": "item_1",
      "text": "클래식한 책상"
    },
    {
      "id": "item_2", 
      "text": "미니멀한 소파"
    }
  ],
  "batch_size": 10
}
```

**응답:**
```json
{
  "results": [
    {
      "id": "item_1",
      "score": 0.75,
      "confidence": 0.82
    },
    {
      "id": "item_2",
      "score": 0.91,
      "confidence": 0.95
    }
  ],
  "total_processed": 2,
  "processing_time": 0.18
}
```

### 스트리밍 추론

```http
POST /stream/infer
Content-Type: application/json
```

**요청:**
```json
{
  "text": "실시간으로 분석할 텍스트",
  "stream_interval": 0.1
}
```

**응답 (Server-Sent Events):**
```
data: {"step": 1, "progress": 0.2, "partial_result": {"score": 0.3}}

data: {"step": 2, "progress": 0.5, "partial_result": {"score": 0.6}}

data: {"step": 3, "progress": 1.0, "final_result": {"score": 0.85, "confidence": 0.92}}
```

## ⚠️ 에러 처리

### 에러 응답 형식

```json
{
  "error": "MODEL_NOT_READY",
  "message": "모델이 아직 로딩 중입니다.",
  "details": {
    "estimated_ready_time": "2024-01-15T10:35:00Z"
  }
}
```

### 주요 에러 코드

- `400 BAD_REQUEST` - 잘못된 요청 형식
- `503 SERVICE_UNAVAILABLE` - 모델이 준비되지 않음
- `429 TOO_MANY_REQUESTS` - 동시 요청 한도 초과
- `500 INTERNAL_SERVER_ERROR` - 모델 추론 오류
- `507 INSUFFICIENT_STORAGE` - GPU 메모리 부족

## 🔄 동시성 제한

### 요청 제한

- **최대 동시 요청**: 2개 (GPU 메모리 제한)
- **대기열 크기**: 10개
- **타임아웃**: 30초

### 큐 관리

```json
{
  "queue_status": {
    "active_requests": 1,
    "queued_requests": 3,
    "max_concurrent": 2,
    "estimated_wait_time": 15.5
  }
}
```

## 🚀 성능 최적화

### GPU 활용

- **CUDA 지원**: NVIDIA GPU 필수
- **메모리 관리**: 자동 메모리 정리
- **배치 처리**: 여러 요청 동시 처리

### 캐싱

- **모델 캐싱**: 메모리에 모델 상주
- **결과 캐싱**: 동일 입력에 대한 결과 캐싱
- **TTL**: 1시간

## 🔧 모니터링

### 메트릭

- **추론 시간**: 평균 50-500ms
- **처리량**: 초당 10-20 요청
- **GPU 사용률**: 실시간 모니터링
- **메모리 사용량**: VRAM 사용량 추적

### 로그

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Inference completed",
  "details": {
    "request_id": "req_123",
    "processing_time": 0.15,
    "model_version": "v1.2.0",
    "gpu_memory_used": "2.1GB"
  }
}
```

## 📱 클라이언트 가이드

### Python 클라이언트

```python
import requests
import asyncio
import aiohttp

class DLAPIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def infer_text(self, text):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/infer",
                json={"text": text},
                headers=self.headers
            ) as response:
                return await response.json()
    
    async def infer_image(self, image_url):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/infer/image",
                json={"image_url": image_url},
                headers=self.headers
            ) as response:
                return await response.json()

# 사용 예시
client = DLAPIClient("http://localhost:8002", "your-api-key")
result = await client.infer_text("모던한 거실")
```

### JavaScript 클라이언트

```javascript
class DLAPIClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  async inferText(text) {
    const response = await fetch(`${this.baseUrl}/infer`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ text })
    });
    return await response.json();
  }

  async streamInfer(text) {
    const response = await fetch(`${this.baseUrl}/stream/infer`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ text })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          console.log('Stream data:', data);
        }
      }
    }
  }
}

// 사용 예시
const client = new DLAPIClient('http://localhost:8002', 'your-api-key');
const result = await client.inferText('모던한 거실');
```

## 🔒 보안

### API 키 관리

- **내부 통신**: CRUD API에서만 접근 가능
- **키 로테이션**: 정기적인 키 갱신
- **접근 로그**: 모든 요청 로깅

### 데이터 보호

- **이미지 처리**: 임시 저장 후 자동 삭제
- **개인정보**: 추론 결과에 개인정보 포함 금지
- **암호화**: HTTPS 통신 필수
