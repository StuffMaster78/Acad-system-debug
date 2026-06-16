# =============================================================================
# essaymaniacs-web — Nuxt 3 marketing site
# Multi-stage build: deps + build in one stage, minimal runtime image.
# =============================================================================

# ── Builder ───────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

RUN npm install -g pnpm@9

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
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
