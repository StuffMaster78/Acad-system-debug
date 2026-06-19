# =============================================================================
# gradecrest-web — Nuxt 3 marketing site
# Multi-stage build: deps + build in one stage, minimal runtime image.
# =============================================================================

# ── Builder ───────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

RUN npm install -g pnpm@9

COPY gradecrest-web/package.json gradecrest-web/pnpm-lock.yaml ./
COPY scripts/patch-nuxt-site-config.mjs /scripts/patch-nuxt-site-config.mjs
RUN pnpm install --frozen-lockfile

ARG NUXT_PUBLIC_API_BASE=https://gradecrest.com
ARG NUXT_PUBLIC_APP_URL=https://app.gradecrest.com
ARG NUXT_PUBLIC_SITE_URL=https://gradecrest.com
ENV NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}
ENV NUXT_PUBLIC_APP_URL=${NUXT_PUBLIC_APP_URL}
ENV NUXT_PUBLIC_SITE_URL=${NUXT_PUBLIC_SITE_URL}

COPY gradecrest-web/ .
RUN pnpm run build

# ── Runner ────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

RUN addgroup -S nuxt && adduser -S -G nuxt nuxt

COPY --from=builder --chown=nuxt:nuxt /app/.output ./.output

USER nuxt

ENV HOST=0.0.0.0 PORT=3000 NODE_ENV=production
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
