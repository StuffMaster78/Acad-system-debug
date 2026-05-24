# Documentation Index

This directory is now treated as living backend and product documentation.

Some older role guides and deployment notes may still describe the removed
legacy frontend. Keep them as reference material only until each document is
reviewed against the redesigned backend and the upcoming fresh frontend.

## Current Planning Docs

- [Packaging Strategy](./PACKAGING_STRATEGY.md) - target repo/package split and
  near-term cleanup rules
- [API Documentation](./API/API_DOCUMENTATION.md) - API reference material
- [Developer Guide](./DEVELOPER/DEVELOPER_GUIDE.md) - backend development notes
- [Deployment Guide](./DEPLOYMENT/DEPLOYMENT_GUIDE.md) - deployment reference

## Role Guides

These guides should be rewritten once the new portals and dashboards are
designed:

- [Client User Guide](./USER_GUIDES/CLIENT_USER_GUIDE.md)
- [Writer User Guide](./USER_GUIDES/WRITER_USER_GUIDE.md)
- [Editor User Guide](./USER_GUIDES/EDITOR_USER_GUIDE.md)
- [Support User Guide](./USER_GUIDES/SUPPORT_USER_GUIDE.md)
- [Admin User Guide](./USER_GUIDES/ADMIN_USER_GUIDE.md)
- [Superadmin User Guide](./USER_GUIDES/SUPERADMIN_USER_GUIDE.md)

## Interactive API Docs

When the backend is running:

- Swagger UI: `/api/v1/docs/swagger/`
- ReDoc: `/api/v1/docs/redoc/`
- OpenAPI Schema: `/api/v1/schema/`

## Documentation Rule

New docs should describe the backend as it exists now or the frontend as it is
being newly designed. Avoid documenting deleted frontend behavior as if it were
still part of the active system.
