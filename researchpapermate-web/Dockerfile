# =============================================================================
# researchpapermate-web — Nuxt 3 marketing site
# Multi-stage build: deps + build in one stage, minimal runtime image.
# =============================================================================

# ── Builder ───────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

RUN npm install -g pnpm@9

COPY researchpapermate-web/package.json researchpapermate-web/pnpm-lock.yaml ./
COPY scripts/patch-nuxt-site-config.mjs /scripts/patch-nuxt-site-config.mjs
RUN pnpm install --frozen-lockfile

ARG NUXT_PUBLIC_API_BASE=https://researchpapermate.com
ARG NUXT_PUBLIC_APP_URL=https://app.researchpapermate.com
ARG NUXT_PUBLIC_SITE_URL=https://researchpapermate.com
ENV NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}
ENV NUXT_PUBLIC_APP_URL=${NUXT_PUBLIC_APP_URL}
ENV NUXT_PUBLIC_SITE_URL=${NUXT_PUBLIC_SITE_URL}

COPY researchpapermate-web/ .
RUN pnpm run build

# ── Runner ────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runner

RUN rm /etc/nginx/conf.d/default.conf
COPY researchpapermate-web/nginx.container.conf /etc/nginx/conf.d/site.conf
COPY --from=builder /app/.output/public /usr/share/nginx/html

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
