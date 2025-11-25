# Dry Run System Setup

This document provides information about the seeded dry run system for end-to-end testing.

## System Overview

The dry run system includes:
- **3 Websites**: Academic Writing Pro, Essay Masters, Paper Experts
- **3 Superadmins** (1 per website)
- **6 Admins** (2 per website)
- **9 Editors** (3 per website)
- **9 Support Staff** (3 per website)
- **100 Clients** (distributed across websites)
- **30 Writers** (10 per website)
- **332 Orders** in various stages

## Login Credentials

All passwords follow the pattern: `[Role]123!`

### Superadmins
- **Academic Writing Pro**: `superadmin@academic-pro.com` / `SuperAdmin123!`
- **Essay Masters**: `superadmin@essay-masters.com` / `SuperAdmin123!`
- **Paper Experts**: `superadmin@paper-experts.com` / `SuperAdmin123!`

### Admins
- `admin1@academic-pro.com` / `Admin123!`
- `admin2@academic-pro.com` / `Admin123!`
- `admin1@essay-masters.com` / `Admin123!`
- `admin2@essay-masters.com` / `Admin123!`
- `admin1@paper-experts.com` / `Admin123!`
- `admin2@paper-experts.com` / `Admin123!`

### Editors
- `editor1@academic-pro.com` / `Editor123!`
- `editor2@academic-pro.com` / `Editor123!`
- `editor3@academic-pro.com` / `Editor123!`
- (and 6 more across other websites)

### Support Staff
- `support1@academic-pro.com` / `Support123!`
- `support2@academic-pro.com` / `Support123!`
- `support3@academic-pro.com` / `Support123!`
- (and 6 more across other websites)

### Clients
- `dryrun.client1@academic-pro.com` / `Client123!`
- `dryrun.client2@academic-pro.com` / `Client123!`
- (and 98 more across all websites)

### Writers
- `dryrun.writer1@academic-pro.com` / `Writer123!`
- `dryrun.writer2@academic-pro.com` / `Writer123!`
- (and 28 more across all websites)

## Order Status Distribution

The system includes orders in the following statuses for comprehensive testing:

- **Initial States**: created (8), pending (8), unpaid (15)
- **Payment & Assignment**: available (14), assigned (29)
- **Active Work**: in_progress (43), on_hold (4), reassigned (4)
- **Submission & Review**: submitted (34), under_review (5), reviewed (6), rated (5), approved (5)
- **Revision States**: revision_requested (18), on_revision (10), revised (10)
- **Editing**: under_editing (17)
- **Final States**: completed (50), closed (25), cancelled (11), refunded (4)
- **Disputes**: disputed (7)

## Frontend Login

### API Configuration
- **Base URL**: `http://localhost:8000`
- **API Endpoint**: `/api/v1/auth/auth/login/`
- **CORS**: Configured to allow `localhost:3000`, `localhost:5173`, and all origins in DEBUG mode

### Login Request Format
```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "remember_me": false
}
```

### Expected Response
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "client",
    "website_id": 1,
    ...
  },
  "expires_in": 3600
}
```

## Troubleshooting

### Frontend Cannot Login

1. **Check Backend is Running**:
   ```bash
   docker-compose ps
   ```
   Ensure `web` service is running on port 8000

2. **Check CORS Settings**:
   - Verify `CORS_ALLOWED_ORIGINS` in `backend/writing_system/settings.py` includes your frontend URL
   - In DEBUG mode, `CORS_ALLOW_ALL_ORIGINS = True` should allow all origins

3. **Check API Endpoint**:
   - Frontend should use: `http://localhost:8000/api/v1/auth/auth/login/`
   - Verify the endpoint is accessible: `curl http://localhost:8000/api/v1/auth/auth/login/`

4. **Check Environment Variables**:
   - Frontend: `VITE_API_BASE_URL=http://localhost:8000` (or set in `.env`)
   - Backend: Ensure database and Redis are accessible

5. **Check Browser Console**:
   - Look for CORS errors
   - Check network tab for failed requests
   - Verify request headers include `Content-Type: application/json`

### Database Issues

If you need to reset the database:
```bash
docker-compose run --rm --no-deps web python manage.py seed_dry_run_system --clear --skip-checks
```

## Running the Seed Command

To seed the system:
```bash
docker-compose run --rm --no-deps -e DB_HOST=db -e REDIS_HOST=redis -e ENABLE_CELERY=0 -e DISABLE_NOTIFICATION_SIGNALS=1 web python manage.py seed_dry_run_system --skip-checks
```

To clear and reseed:
```bash
docker-compose run --rm --no-deps -e DB_HOST=db -e REDIS_HOST=redis -e ENABLE_CELERY=0 -e DISABLE_NOTIFICATION_SIGNALS=1 web python manage.py seed_dry_run_system --clear --skip-checks
```

## Testing Scenarios

With this setup, you can test:

1. **Client Workflow**: Place orders, track status, request revisions
2. **Writer Workflow**: Accept assignments, submit work, handle revisions
3. **Editor Workflow**: Review submissions, assign tasks, manage quality
4. **Support Workflow**: Handle tickets, resolve disputes, assist clients
5. **Admin Workflow**: Manage users, oversee operations, view reports
6. **Superadmin Workflow**: System-wide management, configuration

## Order Lifecycle Testing

The diverse order statuses allow testing of:
- Order creation and payment flow
- Writer assignment and reassignment
- Work in progress and on-hold scenarios
- Submission and review processes
- Revision workflows
- Editing processes
- Completion and closure
- Dispute resolution
- Cancellation and refunds
