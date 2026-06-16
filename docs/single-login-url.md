# Single Login URL — writerscreek.com/login

## What this does

`writerscreek.com/login` is a single entry point for both writers and staff. Users enter their credentials once; the system determines their role and redirects them to the correct portal automatically.

| Role | Lands at |
|---|---|
| `writer` | `app.writerscreek.com` (writer dashboard) |
| `admin` / `superadmin` / `editor` / `support` | `admin.writerscreek.com` (staff dashboard) |

---

## How it works

### 1. Login form (writerscreek.com/login)

The Nuxt marketing site serves a standard email + password form. On submit:

```
POST /api/v1/auth/login/
{ "email": "...", "password": "..." }
```

**Success response:**
```json
{
  "success": true,
  "mfa_required": false,
  "access_token": "<jwt>",
  "refresh_token": "<jwt>"
}
```

### 2. Role resolution

With the access token, the Nuxt page calls:

```
GET /api/v1/users/users/me/
Authorization: Bearer <access_token>
```

Response includes `role` (`writer`, `admin`, `superadmin`, `editor`, `support`).

### 3. Portal redirect

Tokens are placed in the **URL fragment** (hash) of the destination adopt URL:

```
https://app.writerscreek.com/auth/adopt#access=<token>&refresh=<token>
```

or

```
https://admin.writerscreek.com/auth/adopt#access=<token>&refresh=<token>
```

**Why the hash?** Fragment identifiers are never sent to any server — they don't appear in nginx access logs, server-side request logs, or `Referer` headers. The browser never transmits them over the network.

### 4. Token adoption (SPA)

The SPA's existing `/auth/adopt` route (`AdoptTokenView.vue`) handles the handoff:

1. Reads `access` and `refresh` from `window.location.hash`
2. Immediately clears the hash from the address bar via `history.replaceState`
3. Stores tokens in `localStorage`
4. Calls `/api/v1/users/users/me/` to confirm validity and load the user
5. Redirects to the role-appropriate dashboard

### 5. Shared session cookie

Django is configured with:

```
SESSION_COOKIE_DOMAIN = ".writerscreek.com"
CSRF_COOKIE_DOMAIN    = ".writerscreek.com"
```

The leading dot makes the session cookie valid across all `*.writerscreek.com` subdomains. This means a Django session established at `writerscreek.com` is also recognised at `app.writerscreek.com` and `admin.writerscreek.com` — no separate login required if the session is still active.

---

## MFA accounts

Both the MFA challenge and verify endpoints (`/api/v1/auth/mfa/challenge/` and `/api/v1/auth/mfa/verify/`) require the user to already be authenticated. The login endpoint returns `mfa_required: true` without issuing tokens, so the Nuxt page cannot complete the MFA flow inline.

When MFA is required, the login page shows a **portal selector**:

- **Writer portal** → `app.writerscreek.com/auth/login`
- **Staff portal** → `admin.writerscreek.com/auth/login`

Both portals implement the full MFA flow (challenge + code entry). The user completes the verification there as normal.

> MFA is typically enabled on staff/admin accounts. Most writers will not encounter this step.

---

## Sequence diagram

```
Browser                 writerscreek.com        Django
   |                          |                    |
   |-- POST /api/v1/auth/login/ ----------------->|
   |                          |<-- {access, refresh} --|
   |                          |                    |
   |                          |-- GET /api/v1/users/users/me/ (Bearer) ->|
   |                          |<-- { role: "writer" } ------------------|
   |                          |                    |
   |<-- 302 Location: https://app.writerscreek.com/auth/adopt#access=...&refresh=... --|
   |                          |                    |
   |-- (browser follows redirect) ------------------------------------->|
   |   app.writerscreek.com/auth/adopt (SPA reads hash, clears it, stores tokens)
   |                          |                    |
   |-- GET /api/v1/users/users/me/ (Bearer) --------------------------->|
   |<-- { role, email, ... } ------------------------------------------|
   |                          |                    |
   |-- navigate to /writer/dashboard -----------------------------------x
```

---

## Configuration

### Required environment variables

**Backend (`.env`):**

```bash
SESSION_COOKIE_DOMAIN=.writerscreek.com
CSRF_COOKIE_DOMAIN=.writerscreek.com
```

Leave both blank in development. When blank, Django defaults the cookie domain to the request host.

**writerscreek-web (`.env` or Docker):**

```bash
NUXT_PUBLIC_API_BASE=https://writerscreek.com
NUXT_PUBLIC_APP_URL=https://app.writerscreek.com
NUXT_PUBLIC_STAFF_URL=https://admin.writerscreek.com
```

### Docker Compose

The `writerscreek-web` service in `docker-compose.prod.yml` passes all three Nuxt env vars. The backend `web` service picks up `SESSION_COOKIE_DOMAIN` and `CSRF_COOKIE_DOMAIN` from the environment.

### nginx

The `writerscreek.com` server block has a dedicated rate-limited location for auth endpoints:

```nginx
location ~ ^/api/v1/auth/(login|magic-link)/ {
    limit_req zone=auth burst=3 nodelay;  # 5 req/min, burst of 3
    ...
    proxy_pass http://django;
}
```

The more permissive `/api/` block handles all other API traffic. nginx matches the most specific location first, so auth endpoints always get the stricter limit.

---

## Security notes

| Concern | Mitigation |
|---|---|
| Tokens visible in URL bar during redirect | Tokens are in the hash (not path/query), cleared immediately by the adopt page via `history.replaceState`. They never reach any server. |
| Shared session cookie across subdomains | All subdomains are first-party and operator-controlled. Risk surface is equivalent to any multi-subdomain platform (Google, GitHub, etc.). |
| Login brute force | nginx `zone=auth` limits to 5 requests/minute with burst of 3. Django's `LoginRateThrottle` adds a second layer. |
| Staff login exposure | `admin.writerscreek.com` remains available as a direct URL and can be IP-restricted independently (see nginx config comment). The marketing-site login is a convenience path, not the only path. |
| MFA bypass | MFA accounts cannot complete authentication through the marketing-site login page — they are redirected to their portal where the full MFA flow runs. |

---

## Local development

In development the Nuxt devProxy forwards `/api/v1` → `http://localhost:8000`. The login page works against the local Django instance. After a successful login it redirects to either `http://localhost:5173/auth/adopt` or `http://localhost:5173/auth/adopt` (both resolve to the local SPA dev server).

To test the full end-to-end flow locally, override the portal URLs:

```bash
# writerscreek-web/.env
NUXT_PUBLIC_APP_URL=http://localhost:5173
NUXT_PUBLIC_STAFF_URL=http://localhost:5174
```

Tokens will land at the local SPA which handles adoption normally.

---

## Files changed

| File | What changed |
|---|---|
| `writerscreek-web/pages/login.vue` | Real login form replacing the old redirect stub |
| `writerscreek-web/nuxt.config.ts` | `NUXT_PUBLIC_STAFF_URL` added to runtimeConfig |
| `docker-compose.prod.yml` | `NUXT_PUBLIC_STAFF_URL` env var on writerscreek-web service |
| `nginx/nginx.conf` | Auth rate-limit location in writerscreek.com block |
| `backend/writing_system/settings/base.py` | `SESSION_COOKIE_DOMAIN`, `CSRF_COOKIE_DOMAIN` (env-driven, None in dev) |
| `backend/writing_system/settings/production.py` | Both set to `.writerscreek.com` in production |
| `backend/env.template` | Both vars documented with explanation |
