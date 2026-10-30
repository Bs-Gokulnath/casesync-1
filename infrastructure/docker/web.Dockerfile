FROM node:24-slim AS base

WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Next.js resolves next.config.ts's rewrites() once, at build time, into the
# route manifest `next start` serves — not per-request. Bake in the
# container-network hostname so the manifest matches how this image is
# actually run (via docker-compose, never standalone).
ENV API_INTERNAL_URL=http://api:8000
RUN npm run build

FROM base AS runner
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts

EXPOSE 3000
CMD ["npm", "run", "start"]
