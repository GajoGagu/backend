# Gajogagu Server (가져가구)

Monorepo containing two FastAPI services and deployment assets.

- CRUD API: marketplace backend (users, products, wishlist, orders, rider flows, notifications, uploads)
- DL API: deep-learning inference (detection/similarity)

## Local run (Docker Compose)
- CPU: `docker compose -f deploy/compose/docker-compose.cpu.yaml up --build`
- GPU: `docker compose -f deploy/compose/docker-compose.gpu.yaml up --build`

Ports (local)
- CRUD API: http://localhost:8001
- DL API: http://localhost:8002
