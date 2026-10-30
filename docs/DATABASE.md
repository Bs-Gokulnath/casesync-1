# Database Design — AICTE CaseWatch

PostgreSQL 16. All tables have `created_at timestamptz default now()`; mutable
tables also have `updated_at timestamptz` maintained by the ORM. All ids are
`BIGINT GENERATED ALWAYS AS IDENTITY` unless noted. Soft-deletable
operational tables carry `is_active` (institutions, users, bureaus, regions,
categories) or `is_deleted` (documents) instead of hard delete.
`audit_events` is append-only: no API route ever issues UPDATE/DELETE against
it, and the ORM model has no update/delete repository methods for it.

## Reference tables
- **bureaus**(id, code UNIQUE, name, description, is_active, created_at, updated_at)
- **regions**(id, code UNIQUE, name, is_active, created_at, updated_at)
- **complaint_categories**(id, code UNIQUE, name, description, is_active, created_at, updated_at)
- **sla_policies**(id, category_id FK→complaint_categories NULL, priority,
  days_to_resolve, warning_days_before, is_active, created_at, updated_at)
  — UNIQUE(category_id, priority); a NULL category_id row is the default
  fallback policy for that priority.

## Identity & access
- **users**(id, employee_code UNIQUE, full_name, email UNIQUE, password_hash,
  role ENUM(system_admin, senior_management, bureau_officer, regional_officer,
  auditor), bureau_id FK→bureaus NULL, region_id FK→regions NULL, is_active,
  created_at, updated_at)
- **sessions**(id, token_hash UNIQUE, user_id FK→users, csrf_token,
  user_agent, ip_address, expires_at, last_seen_at, created_at) — looked up by
  hash of the cookie value, never the raw token.

## Institutions
- **institutions**(id, institution_code UNIQUE, aicte_permanent_id UNIQUE
  NULL, name, normalized_name INDEXED, address, region_id FK→regions,
  contact_email NULL, contact_phone NULL, is_active, created_at, updated_at)
- **institution_aliases**(id, institution_id FK→institutions, alias_name,
  normalized_alias INDEXED) — alternate/previous names feeding deterministic
  matching.

## Complaints & workflow
- **complaints**(id, case_reference UNIQUE, institution_id FK→institutions,
  category_id FK→complaint_categories, subject, normalized_subject INDEXED,
  description, source ENUM(portal, email, letter, phone, walk_in, other),
  priority ENUM(low, medium, high, critical), status ENUM(received,
  under_review, under_process, pending_information, transferred, escalated,
  disposed), bureau_id FK→bureaus, assigned_officer_id FK→users NULL,
  received_date date, expected_disposal_date date NULL, last_action_at
  timestamptz NULL, last_action_note text NULL, next_action_note text NULL,
  disposal_note text NULL, is_deleted boolean default false, created_by
  FK→users, created_at, updated_at)
- **case_assignments**(id, complaint_id FK→complaints, officer_id FK→users,
  bureau_id FK→bureaus, assigned_by FK→users, assigned_at, unassigned_at
  NULL, is_current boolean) — history of who held a case; exactly one
  `is_current=true` row per open complaint.
- **case_status_history**(id, complaint_id FK→complaints, from_status NULL,
  to_status, actor_id FK→users, reason NULL, created_at)
- **case_action_history**(id, complaint_id FK→complaints, action_type
  ENUM(transfer, escalate, dispose, reopen, note, assign), actor_id FK→users,
  from_bureau_id FK→bureaus NULL, to_bureau_id FK→bureaus NULL, reason NULL,
  note NULL, created_at)
- **case_relationships**(id, complaint_id FK→complaints, related_complaint_id
  FK→complaints, relationship_type ENUM(related, duplicate), created_by
  FK→users, created_at) — UNIQUE(complaint_id, related_complaint_id); kept
  symmetric at the service layer (one logical link, two readable directions).

## Overlap detection
- **overlap_alerts**(id, institution_id FK→institutions, matching_signals
  JSONB, confidence_score numeric(4,3), rationale text, status
  ENUM(open, confirmed, dismissed, resolved), decided_by FK→users NULL,
  decision_reason NULL, decided_at NULL, created_at, updated_at)
- **overlap_alert_cases**(id, overlap_alert_id FK→overlap_alerts, complaint_id
  FK→complaints) — UNIQUE(overlap_alert_id, complaint_id); ≥2 rows per alert.

## Documents
- **documents**(id, complaint_id FK→complaints, file_name, stored_path
  (relative, outside any public web root), content_type, size_bytes,
  uploaded_by FK→users, uploaded_at, is_deleted boolean default false)

## Notifications & audit
- **notifications**(id, user_id FK→users NULL, bureau_id FK→bureaus NULL,
  type ENUM(overlap_alert, assignment, deadline_warning, overdue, transfer,
  escalation), title, message, related_complaint_id FK→complaints NULL,
  related_overlap_alert_id FK→overlap_alerts NULL, is_read boolean default
  false, created_at) — a notification targets a user OR a whole bureau
  (fan-out read is computed, not duplicated per user).
- **audit_events**(id, actor_id FK→users NULL, action, entity_type, entity_id,
  before_json JSONB NULL, after_json JSONB NULL, ip_address NULL, created_at)
  — append-only; `before_json`/`after_json` never include `password_hash` or
  session tokens.

## Indexes (beyond PK/FK/UNIQUE above)
`complaints(status)`, `complaints(bureau_id, status)`,
`complaints(assigned_officer_id)`, `complaints(institution_id)`,
`complaints(expected_disposal_date)`, `overlap_alerts(status)`,
`audit_events(entity_type, entity_id)`, `notifications(user_id, is_read)`.

## Deletion/retention policy
Operational entities (institutions, users, bureaus, regions, categories) are
deactivated (`is_active=false`), never hard-deleted, so historical complaints
keep valid foreign keys. Documents are soft-deleted (`is_deleted=true`) and
the underlying file is retained for audit purposes; a future retention job
(out of scope for this build) would purge after a configured period.
`audit_events` rows are never deleted through the application.

## Migrations
All schema changes go through Alembic (`apps/api/alembic/versions`). No
production schema is ever edited by hand.
