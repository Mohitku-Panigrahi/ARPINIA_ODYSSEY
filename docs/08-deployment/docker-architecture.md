# Docker Architecture & Network Security

## Network Topology
Docker Compose will define two networks:
1. `frontend-net`: Bridging the public internet (via reverse proxy/Nginx) to `apps/web` and `services/api`.
2. `backend-net`: Isolated. Bridging `services/api`, `services/worker`, `services/ai-engine`, `database`, and `redis`.

## Security Rule
- `database` and `redis` MUST NOT expose ports to `frontend-net` or the host (0.0.0.0). They belong strictly to `backend-net`.
- `services/api` acts as the sole gateway.

## Environment Variables
- Secrets are injected at runtime via `.env` files matching `.env.example`.
- Docker images must not bake secrets into the layers.
