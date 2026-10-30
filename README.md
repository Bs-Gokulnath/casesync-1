# AICTE CaseWatch

An integrated dashboard for monitoring and tracking institution-related
complaint cases across AICTE bureaus and cells (Regional Bureaus, PGRC, and
other configured cells), built for SIH26264.

It gives authorized AICTE staff one place to look up an institution's full
complaint history across bureaus, run complaints through a controlled
workflow, see cross-bureau overlap alerts, track SLA compliance, and review
an immutable audit trail — see `docs/PRD.md` for the full problem framing and
`docs/ARCHITECTURE.md` / `docs/DATABASE.md` / `docs/API_SPEC.md` for the
technical design.

**This is a real, working application**, not a mockup: every number on the
dashboard is a live query against Postgres, every button either performs a
real backend mutation or is hidden from roles that can't use it, and the
demo data below is clearly fictional (see `docs/IMPLEMENTATION_PLAN.md` for
the phase-by-phase build log and what's verified).

## Stack

- **Frontend**: Next.js 16 (App Router) / React 19 / TypeScript (strict),
  Tailwind CSS v4, shadcn/ui, TanStack Table v8, Recharts, React Hook Form +
  Zod.
- **Backend**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL 16.
- **Auth**: opaque server-side session cookie (HttpOnly) + double-submit CSRF
  cookie, Argon2 password hashing, backend-enforced RBAC.
- **Infra**: Docker Compose (Postgres + API + Web).

## Running it

### Option A — Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec api python -m scripts.seed   # fictional demo data, local dev only
```

- Web: http://localhost:3000
- API docs: http://localhost:8000/api/v1/docs

### Option B — running each service locally

```bash
# Postgres only, via Docker
docker compose up -d postgres

# Backend
cd apps/api
python -m venv .venv && .venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd apps/web
npm install
npm run dev
```

## Demo credentials

Every seeded account shares the password **`Demo@12345`**:

| Email | Role |
|---|---|
| `admin@aictecasewatch-demo.org` | System Administrator |
| `management@aictecasewatch-demo.org` | Senior Management |
| `rb.officer@aictecasewatch-demo.org` | Bureau Officer (Regional Bureau — Delhi) |
| `pgrc.officer@aictecasewatch-demo.org` | Bureau Officer (PGRC) |
| `regional.officer@aictecasewatch-demo.org` | Regional Officer (Northern Region) |
| `auditor@aictecasewatch-demo.org` | Auditor (read-only) |

The seed script (`apps/api/scripts/seed.py`) creates fictional bureaus,
regions, categories, institutions and demonstrates every scenario the brief
calls for: the same institution with open cases in two bureaus (open overlap
alert), a confirmed duplicate, a dismissed false positive, an overdue case,
a transferred case, and a disposed case. It refuses to run when
`APP_ENV=production` and is idempotent — re-running it updates nothing and
creates nothing twice.

## Tests

```bash
# Backend — from apps/api, with the venv active and Postgres reachable
pytest                       # 63 tests: unit + integration (auto-creates a
                              # dedicated <dbname>_test database, isolated
                              # from any seeded dev data)
ruff check . && black --check . && mypy app

# Frontend — from apps/web
npm run typecheck
npm run lint
npm run test                 # vitest
npm run build                # production build
npm run test:e2e             # Playwright — needs the full docker-compose
                              # stack running and seeded (see e2e/README)
```

**Verified while building this** (see `docs/IMPLEMENTATION_PLAN.md` for the
full log): all of the above pass; the full docker-compose stack was smoke
tested end-to-end with curl through the actual browser-facing proxy (not the
container network directly) as every seeded role, including a real
multipart document upload/download round trip and a real
`POST /api/v1/institutions` write with CSRF enforcement.

## Project structure

```
apps/web/     Next.js app — see src/app (routes), src/features (feature
              modules: forms, tables, API calls), src/components (shared
              UI), src/lib (typed API clients, auth session helper)
apps/api/     FastAPI app — see app/api/v1/endpoints (thin routers),
              app/services (business rules), app/repositories (queries
              only), app/models (SQLAlchemy), app/schemas (Pydantic)
infrastructure/docker/   Dockerfiles
docs/         PRD, architecture, database design, API spec, phase-by-phase
              implementation log
```

See the root `CLAUDE.md` for architecture rules, coding conventions, and
testing requirements followed throughout this codebase.

## Known limitations

- **No email/SMS delivery.** Notifications are in-app only
  (`notifications` table), generated synchronously when the triggering
  action happens (assignment, transfer, escalation, a new overlap alert).
  There is no background scheduler in this build, so approaching-deadline
  and overdue notifications are **not** persisted rows — they're computed
  live in the Work Queue's "Overdue" tab instead. Adding a scheduled job
  (Celery/APScheduler) to also persist those as notifications is the
  natural next step.
- **CSV export covers complaints only** (not a full multi-sheet report).
- **Individual complaint/institution reads, and workflow actions
  (transition/transfer/escalate/dispose/assign), are not bureau/region-
  scoped** — only the *list* endpoints (`GET /complaints`, work queue) are.
  A user with `complaint:transition` can act on any complaint by ID even
  if it belongs to a different bureau. Tightening this to match the
  list-level scoping is a reasonable follow-up.
- **Playwright specs cover the five flows the brief calls out** (login,
  create complaint, transfer, overlap review, disposal) but are not an
  exhaustive UI regression suite.
- Demo/seed data is fictional and is not meant to resemble any real
  institution, complaint, or person.
