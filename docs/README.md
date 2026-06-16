# Documentation Index

## Architecture & Diagrams

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — System overview, order lifecycle state machine, notification pipeline, compensation flow, authentication sequence, multi-tenant portal routing, and ER diagram. All diagrams use Mermaid.

## Reference Docs

- [API Documentation](./API/API_DOCUMENTATION.md) — API contract and endpoint reference
- [Developer Guide](./DEVELOPER/DEVELOPER_GUIDE.md) — Backend development notes, conventions, testing
- [Deployment Guide](./DEPLOYMENT/DEPLOYMENT_GUIDE.md) — Production deployment (Docker, nginx, SSL, Stripe)
- [Infrastructure Guide](./DEPLOYMENT/INFRASTRUCTURE.md) — DigitalOcean sizing, managed services, cost tiers
- [Uptime Kuma Setup](./DEPLOYMENT/UPTIME_KUMA_SETUP.md) — Monitoring configuration
- [Admin Workflows](./ADMIN_WORKFLOWS.md) — Staff operation playbooks
- [Single Login URL](./single-login-url.md) — How writerscreek.com/login routes writers and staff to their portals

## User Guides

- [Client User Guide](./USER_GUIDES/CLIENT_USER_GUIDE.md)
- [Writer User Guide](./USER_GUIDES/WRITER_USER_GUIDE.md)
- [Editor User Guide](./USER_GUIDES/EDITOR_USER_GUIDE.md)
- [Support User Guide](./USER_GUIDES/SUPPORT_USER_GUIDE.md)
- [Admin User Guide](./USER_GUIDES/ADMIN_USER_GUIDE.md)
- [Superadmin User Guide](./USER_GUIDES/SUPERADMIN_USER_GUIDE.md)

## Interactive API Docs (live server)

| URL | Tool |
|-----|------|
| `/api/v1/docs/swagger/` | Swagger UI |
| `/api/v1/docs/redoc/` | ReDoc |
| `/api/v1/schema/` | OpenAPI schema (JSON) |
