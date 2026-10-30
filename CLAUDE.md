# CLAUDE.md — AICTE CaseWatch

Monorepo: `apps/web` (Next.js/TS) + `apps/api` (FastAPI/Python) +
PostgreSQL, orchestrated with Docker Compose. Full design docs in `docs/`
(`PRD.md`, `ARCHITECTURE.md`, `DATABASE.md`, `API_SPEC.md`,
`IMPLEMENTATION_PLAN.md`) — read them before large changes.

## Commands
```bash
# whole stack
docker compose up -d                 # postgres + api + web
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py

# backend (apps/api), local venv
python -m venv .venv && .venv/Scripts/activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest                                # unit + integration (needs DB)
ruff check . && black --check . && mypy app

# frontend (apps/web)
npm install
npm run dev                          # http://localhost:3000
npm run lint && npm run typecheck
npm run test                         # vitest
npm run test:e2e                     # playwright (needs full stack up)
npm run build
```

## Architecture rules
- Browser talks only to the Next.js origin. `next.config.js` rewrites
  `/api/*` to the FastAPI service. Never call the API cross-origin from a
  client component; never put secrets in `NEXT_PUBLIC_*`.
- API layering is one-directional: `api/v1/endpoints` → `services` →
  `repositories` → SQLAlchemy models. Endpoints validate input/output with
  Pydantic schemas and never touch the DB session directly. Services hold
  business rules (workflow legality, SLA math, permission scoping, overlap
  rules). Repositories are pure query code, no business logic.
- Authorization is backend-only. Every mutating/sensitive endpoint declares
  its required permission via the `require_permission(...)` FastAPI
  dependency (`app/security/permissions.py`). Frontend role checks are UX
  hints, never the security boundary — do not add a feature that is "hidden
  but technically reachable" without a matching backend check.
- Every service method that mutates state writes one `audit_events` row in
  the same DB transaction. `audit_events` has no update/delete path —
  don't add one.
- Workflow transitions are only legal per the matrix in
  `app/services/workflow_service.py`; don't bypass it by setting
  `complaint.status` directly anywhere else.
- Session auth: HttpOnly session cookie + readable CSRF cookie
  (double-submit). State-changing requests must include the CSRF header;
  don't disable this check to "make a test pass."

## Coding rules
- TypeScript strict mode; no `any` without a comment explaining why. Feature
  code lives under `src/features/<feature>/` (components, hooks, schemas,
  api client); shared primitives under `src/components/`.
- Python: type hints everywhere, Pydantic v2 schemas for all I/O, no bare
  `except:`. Keep files cohesive — split a service/router before it becomes a
  junk drawer.
- No hardcoded metrics/demo numbers in UI code — every dashboard value comes
  from an API response. Demo data only enters via `scripts/seed.py`, and the
  UI labels it as demo/seed data.
- Don't add abstractions, config flags, or "future-proofing" beyond what the
  current phase needs.

## Testing requirements
- New service-layer logic (workflow transitions, SLA calc, matching,
  permissions, CSV export sanitization) needs a pytest unit test.
- New API endpoints with real DB effects need an integration test against
  the dockerized Postgres.
- New non-trivial forms/components need a Vitest + RTL test.
- Critical end-to-end flows (login, create complaint, transfer, overlap
  review, disposal) are covered by Playwright specs in `apps/web/e2e/`.
- Run the relevant suite after every change; report actual pass/fail, never
  assume. If a suite can't run in the current environment (e.g. no Docker),
  say so explicitly instead of claiming it passed.

## Current status
See `docs/IMPLEMENTATION_PLAN.md` for phase-by-phase progress and the
precise next steps if work is picked up mid-way.
