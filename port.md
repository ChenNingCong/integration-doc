| Backend URL | Port | Route | Description |
|---|---|---|---|
| `http://localhost:3000` | 3000 | `/*` | Frontend Page |
| `http://localhost:8080` | 8080 | `/api/health` | Self-referencing Gateway |
| `http://localhost:8001` | 8001 | `/api/auth/*` | Auth Microservice |
| `http://localhost:8002` | 8002 | `/api/users/*` | User Microservice |
| `http://localhost:8003` | 8003 | `/api/posts/*`, `/api/replies/*` | Post & Reply Microservice |
| `http://localhost:8004` | 8004 | `/api/messages/*` | Message Microservice |
| `http://localhost:8005` | 8005 | `/api/history/*` | History Microservice |
| `http://localhost:8006` | 8006 | `/api/files/*` | File Microservice |