# 가구 마켓플레이스 API (Furniture Marketplace API)
Two FastAPI services in one monorepo: Marketplace API and DL Inference API. Build CPU/GPU images, run via Compose or Kustomize.

## Services
- **Marketplace API** (`services/crud-api/`) - Korean furniture marketplace with user/rider auth, products, cart, orders, AI recommendations
- **DL API** (`services/dl-api/`) - Deep learning inference service with async processing  

## Local (Compose)
- CPU: `docker compose -f deploy/compose/docker-compose.cpu.yaml up --build`
- GPU: `docker compose -f deploy/compose/docker-compose.gpu.yaml up --build`

## Service Ports
- Marketplace API: http://localhost:8001
- DL API: http://localhost:8002  

## Kubernetes (Kustomize)
- Marketplace: `kubectl apply -k deploy/k8s/overlays/cpu`
- DL:   `kubectl apply -k deploy/k8s/overlays/gpu`

## Images
- ghcr.io/ORG/myapp-crud:latest (Marketplace API)
- ghcr.io/ORG/myapp-dl:latest

## Marketplace API Features
- **Authentication**: Separate user/rider accounts with JWT tokens
- **Social Login**: Google/Kakao OAuth integration
- **Products**: Furniture catalog with categories, search, filters
- **Wishlist**: Save favorite products
- **Cart**: Shopping cart with shipping calculations
- **Orders**: Order management with rider assignment
- **Payments**: PG integration (card, KakaoPay, NaverPay)
- **Notifications**: User notifications system
- **AI Recommendations**: Style matching based on room images
- **File Uploads**: Image upload with pre-signed URLs
