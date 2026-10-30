# API Specification — AICTE CaseWatch (v1)

Base path: `/api/v1`. JSON in/out. Errors: `{"detail": "...", "code": "..."}`
with correct HTTP status (400 validation, 401 unauthenticated, 403
unauthorized, 404 not found, 409 conflict, 422 schema). List endpoints share
`?page=1&page_size=20&sort=-created_at&...filters` and return
`{"items": [...], "total": N, "page": 1, "page_size": 20}`.

## Auth — `/auth`
- `POST /auth/login` {email, password} → sets session + csrf cookies, returns user profile.
- `POST /auth/logout` → revokes session server-side.
- `GET /auth/me` → current user profile + permissions.

## Overview — `/overview`
- `GET /overview/metrics` → totals (received/pending/under_process/disposed/
  transferred/overdue), disposal rate, open overlap alert count — all scoped
  to the caller's bureau/region unless they hold an org-wide permission.
- `GET /overview/trends?days=30` → daily received vs disposed series.
- `GET /overview/bureau-workload`, `GET /overview/ageing-buckets`,
  `GET /overview/region-breakdown`, `GET /overview/recent-activity`.

## Institutions — `/institutions`
- `GET /institutions` (search, region, is_active filters)
- `POST /institutions` (create — requires `institution:write`)
- `GET /institutions/{id}` (profile + complaint history summary)
- `PATCH /institutions/{id}` (edit)
- `PATCH /institutions/{id}/status` (activate/deactivate, reason required)
- `POST /institutions/{id}/aliases`

## Complaints — `/complaints`
- `GET /complaints` (filters: status, bureau_id, priority, category_id,
  institution_id, assigned_officer_id, q, date range)
- `POST /complaints` (create; triggers overlap scan)
- `GET /complaints/{id}` (detail incl. assignment, history, documents, related cases, active overlap alerts)
- `PATCH /complaints/{id}` (edit mutable fields; audited)
- `POST /complaints/{id}/transition` {to_status, reason?} — validated against
  the workflow matrix in `services/workflow_service.py`.
- `POST /complaints/{id}/transfer` {to_bureau_id, reason}
- `POST /complaints/{id}/escalate` {reason}
- `POST /complaints/{id}/dispose` {disposal_note}
- `POST /complaints/{id}/reopen` {reason} — requires `case:reopen` permission.
- `POST /complaints/{id}/assign` {officer_id}
- `GET /complaints/{id}/relationships` / `POST /complaints/{id}/relationships`
  {related_complaint_id, relationship_type} — kept symmetric (one logical
  link, both complaints list it); separate from overlap alerts, which are
  system-detected and never auto-merge or relate cases themselves.
- `GET /complaints/{id}/documents` / `POST /complaints/{id}/documents`
  (multipart upload, content-type allowlist + size limit enforced)
- `GET /complaints/{id}/documents/{doc_id}` (authenticated download)

## Overlaps — `/overlaps`
- `GET /overlaps` (filters: status, institution_id)
- `GET /overlaps/{id}`
- `POST /overlaps/{id}/decision` {status: confirmed|dismissed|resolved, reason}

## Work queue — `/work-queue`
- `GET /work-queue/mine`, `GET /work-queue/bureau`,
  `GET /work-queue/overdue`, `GET /work-queue/unassigned`

## Notifications — `/notifications`
- `GET /notifications` (mine, paginated, unread filter)
- `POST /notifications/{id}/read`, `POST /notifications/read-all`

## Analytics — `/analytics`
- `GET /analytics/summary?from=&to=&bureau_id=&region_id=&category_id=`
- `GET /analytics/export.csv?...same filters` — permission-checked,
  CSV-injection-sanitized.

## Administration — `/admin`
- CRUD under `/admin/bureaus`, `/admin/regions`, `/admin/categories`,
  `/admin/sla-policies`, `/admin/users` — all `system_admin` only.

## Audit — `/audit-logs`
- `GET /audit-logs` (filters: entity_type, entity_id, actor_id, date range) —
  read-only, `audit:read` permission (auditor, senior_management, system_admin).

Full interactive schema is served by FastAPI at `/api/v1/openapi.json` and
`/api/v1/docs` once the backend is running.
