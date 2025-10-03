# 가져가구 API (Gajogagu API)
Two FastAPI services in one monorepo: CRUD API and DL Inference API. Build CPU/GPU images, run via Compose or Kustomize.

## Services
- **CRUD API** (`services/crud-api/`) - Korean furniture marketplace with user/rider auth, products, cart, orders, AI recommendations
- **DL API** (`services/dl-api/`) - Deep learning inference service with async processing  

## Local (Compose)
- CPU: `docker compose -f deploy/compose/docker-compose.cpu.yaml up --build`
- GPU: `docker compose -f deploy/compose/docker-compose.gpu.yaml up --build`

## Service Ports
- CRUD API: http://localhost:8001
- DL API: http://localhost:8002  

## Deployment
Use Docker Compose for local and server deployments. Kubernetes/Kustomize configs have been removed.

## Images
- ghcr.io/gajogagu/myapp-crud:latest (CRUD API)
- ghcr.io/gajogagu/myapp-dl:latest

## CRUD API Features
- **Authentication**: Separate user/rider accounts with JWT tokens
- **Products**: Furniture catalog with categories, search, filters
- **Wishlist**: Save favorite products
- **Cart**: Shopping cart with shipping calculations
- **Orders**: Order management with rider assignment
- **Payments**: PG integration (card, KakaoPay, NaverPay)
- **Notifications**: User notifications system
- **AI Recommendations**: Style matching based on room images
- **File Uploads**: Image upload with pre-signed URLs
