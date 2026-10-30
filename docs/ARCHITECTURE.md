# Architecture — AICTE CaseWatch

## 1. Stack
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript (strict),
  Tailwind CSS, shadcn/ui primitives, Lucide icons, TanStack Table, Recharts,
  React Hook Form + Zod, Sonner (toasts).
- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0 (sync ORM,
  psycopg3 driver), Alembic migrations, PostgreSQL 16.
- **Auth**: opaque server-side session tokens in an HttpOnly, SameSite=Lax
  cookie, validated against a `sessions` table on every request (not JWT —
  this project needs instant server-side revocation, e.g. deactivating a
  user). A separate, readable `csrf_token` cookie implements double-submit
  CSRF protection for state-changing requests.
- **Infra**: Docker Compose for Postgres + API + Web, with health checks.

## 2. Why these choices
- **Sync SQLAlchemy over async**: the workload is CRUD + reporting queries,
  not high-concurrency I/O; sync keeps the service/repository layer simple
  and testable with plain pytest fixtures, no event-loop edge cases.
- **Opaque session over JWT**: a supervisor must be able to deactivate an
  officer and have their session die immediately (JWT access tokens would
  stay valid until expiry unless we maintain a blocklist anyway — which is
  just a sessions table with extra steps).
- **Next.js rewrite proxy, not CORS**: `next.config.js` rewrites `/api/*` to
  the FastAPI origin, so the browser only ever talks to one origin. This
  avoids SameSite=None/cross-site cookie problems in both dev and prod and
  removes an entire class of CORS misconfiguration risk. Server Components
  call the API directly (container-to-container URL) and forward the
  incoming cookie header.
- **Deterministic matching first**: overlap/duplicate detection is rule-based
  (exact ID, normalized name, alias table, category + text similarity) so it
  is explainable and testable. An optional TF-IDF cosine-similarity signal is
  layered on top, off by default without extra config, never a hard
  dependency, and always labelled a suggestion for human review.

## 3. Monorepo layout
```
apps/web/        Next.js app (see src/app, src/features, src/components, src/lib)
apps/api/         FastAPI app (app/core, db, models, schemas, repositories,
                  services, api/v1/endpoints, security, middleware, tests)
infrastructure/docker/   Dockerfiles for web/api, Postgres init
scripts/          dev/seed/check helper scripts
docs/             this documentation set
docker-compose.yml, .env.example, CLAUDE.md, README.md
```

## 4. Request flow
Browser → Next.js (same-origin) → `/api/*` rewrite → FastAPI →
`api/v1/endpoints/*` (thin, validates input via Pydantic schema) →
`services/*` (business rules: workflow legality, SLA calc, overlap rules,
permission checks) → `repositories/*` (SQLAlchemy queries only, no business
logic) → Postgres. Every service call that mutates state writes one row to
`audit_events` in the same DB transaction.

## 5. AuthZ model
Permissions are defined once as a matrix in
`apps/api/app/security/permissions.py` (`Role -> set[Permission]`) and
enforced via a FastAPI dependency (`require_permission(Permission.X)`) on
every router that mutates or reads scoped data. Bureau Officers and Regional
Officers are additionally scoped to their own `bureau_id`/`region_id` inside
the repository query (`WHERE bureau_id = :officer_bureau` unless the caller
has an org-wide permission). This scoping is implemented in the service
layer, never trusted from a client-supplied filter.

## 6. Overlap detection pipeline
1. On complaint create/update, `OverlapService` looks for other **open**
   complaints against the same `institution_id` in a *different* bureau.
2. Deterministic signals computed: same institution (always true by query),
   same category, normalized-subject Jaccard/substring match, received-date
   proximity (≤30 days). Each signal has a weight; total score ≥ threshold
   (configurable, default 0.55) creates/updates an `overlap_alerts` row with
   `matching_signals` JSON (which signals fired) and a human-readable
   rationale string — never a black-box number alone.
3. Alerts are surfaced wherever either case is viewed and in a dedicated
   Overlaps page. A user with `overlap:decide` permission marks the alert
   CONFIRMED / DISMISSED / RESOLVED with a mandatory reason; this never
   mutates the underlying complaints, merges records, or changes status.

## 7. Testing strategy
- **pytest unit**: matching service, SLA calculator, permission matrix,
  workflow transition table, CSV-export sanitizer.
- **pytest integration**: auth flow, complaints CRUD, workflow endpoints,
  overlap endpoints — against a real Postgres (docker) test database.
- **Vitest + RTL**: critical forms (complaint create/edit, transfer dialog)
  and the overlap alert card.
- **Playwright**: login → create complaint → transfer → overlap review →
  disposal, run against the dockerized stack.

## 8. Next.js 16 specifics (confirmed from the installed framework's docs)
The scaffold installed Next.js 16.4.3 / React 19.3 (the current stable
release at the time this project was built — `create-next-app@14` was
rejected after `npm audit` showed outstanding high/critical advisories across
that major that are fixed in current `next`). Two 16-specific decisions:
- **Cache Components (`cacheComponents: true`) is left OFF.** It is Next 16's
  new opt-in partial-prerendering model, which requires wrapping every
  component that reads `cookies()`/`headers()`/DB data in `<Suspense>` to
  avoid build/dev errors. Since literally every route in CaseWatch is behind
  auth and reads per-request Postgres state, there is no static shell to gain
  and it would add ceremony everywhere for no benefit. We use the documented
  "previous model" instead: a Server Component that calls `cookies()` or
  fetches per-request data is dynamic by default, no directive needed.
- **Middleware is called "Proxy"** in 16 (`proxy.ts`, same capabilities as
  the old `middleware.ts`). Used only for an optimistic logged-out redirect
  (`has the session cookie at all?`) — never for the real authorization
  decision, which always happens server-side against the `sessions` table via
  the API.
**Gotcha confirmed by building this project**: `next.config.ts`'s `rewrites()`
is resolved once into a static route manifest at `next build` time, not
re-evaluated per request by `next start`. The web Dockerfile therefore bakes
`API_INTERNAL_URL=http://api:8000` (the compose network hostname) as a build
`ENV` before `npm run build`, rather than relying on the runtime container
environment — setting it only via `docker-compose.yml`'s `environment:` block
has no effect on the already-built manifest.

**`@tanstack/react-table` is pinned to `^8`**, not the registry's current
`^9`. v9 renamed the entire hook API (`useReactTable`→`ReactTable`,
`getCoreRowModel`→`createCoreRowModel`, a v8-compatible shim only exists
under a separate `/legacy` entry point) in a way with no reliable prior
documentation to build against; v8 is still maintained, fully type-checks,
and is what every data table in this app (`InstitutionsTable`,
`ComplaintsTable`) is built on.

`params`/`searchParams` in pages and layouts are `Promise`s (`await` them) —
unchanged from Next 15, still true in 16, and is why generated types use
`LayoutProps<'/route'>` / `PageProps<'/route'>` helpers instead of hand
written prop types.

## 9. Environments
`development` and `production` configs are both read from environment
variables via `app/core/config.py` (`pydantic-settings`), never branched with
`if DEBUG` scattered through the codebase. `.env.example` documents every
variable with a safe placeholder; no real secret is ever committed.
