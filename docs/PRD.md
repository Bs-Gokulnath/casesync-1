# Product Requirements Document — AICTE CaseWatch

## 1. Problem (SIH26264)
AICTE's Regional Bureaus (RB), Public Grievance Redressal Cells (PGRC) and other
bureaus/cells handle institution-related complaints independently. There is no
shared view of which institution has open cases across bureaus, no shared SLA
tracking, and no systematic way to detect that two bureaus are working the same
underlying issue (or a duplicate complaint) for the same institution.

## 2. Goal
A single internal web application — **AICTE CaseWatch** — that gives authorized
AICTE staff one place to:
- Look up any institution and see its full complaint history across bureaus.
- Register, assign, and progress complaints through a controlled workflow.
- See cross-bureau overlap alerts for the same institution and decide on them.
- Track SLA compliance, ageing, workload, and disposal performance.
- Review an immutable audit trail of who did what, when.

Out of scope: public-facing complaint submission portal, automatic case
merging, automated regulatory action, email/SMS delivery (unless a provider is
actually configured), and any claim of "AI-detected" overlaps beyond the
documented deterministic + optional similarity rules.

## 3. Users & Roles
| Role | Description | Key capabilities |
|---|---|---|
| System Administrator | IT/admin staff | Manage users, roles, bureaus, regions, categories, SLA policies |
| Senior Management | AICTE leadership | Read all data, analytics, exports, overlap decisions |
| Bureau Officer | RB/PGRC/other bureau staff | Manage complaints assigned to their bureau, workflow actions |
| Regional Officer | Region-scoped staff | Manage institutions/complaints in their region |
| Auditor (read-only) | Compliance/audit staff | Read-only access to all data + audit logs, no mutations |

## 4. Core User Stories (acceptance-mapped)
1. As a bureau officer, I can register a complaint against an institution and
   it immediately appears in my bureau's work queue. *(Complaint CRUD)*
2. As a bureau officer, I can move a case through received → under review →
   under process → disposed, and the system blocks moves that skip required
   steps. *(Workflow engine)*
3. As any officer, when I open an institution with cases in both RB and PGRC,
   I see a visible "Potential Overlapping Cases — Coordination Required"
   banner with the matching rationale. *(Overlap detection)*
4. As senior management, I can see bureau-wise and region-wise pending/overdue
   counts and export them to CSV. *(Analytics/export)*
5. As an auditor, I can see the full history of a case including every status
   change, transfer, and overlap decision, with actor and timestamp, and I
   cannot edit anything. *(Audit log, RBAC)*
6. As a system administrator, I can add a new bureau/region/category and set
   its SLA threshold without a deploy. *(Administration)*

## 5. Non-functional requirements
- Backend-enforced authorization on every mutating endpoint — the frontend
  hiding a button is UX only, never the security boundary.
- All timestamps stored UTC, timezone-aware; displayed in IST in the UI.
- No hardcoded dashboard numbers — every metric is a query over persisted
  rows, clearly derived from (seeded, fictional) demo data in this build.
- Append-only audit log; no UPDATE/DELETE route ever touches `audit_events`.
- CSV exports must neutralize leading `= + - @` characters (formula
  injection) and must respect the caller's data scope.
- Responsive at 1440px / 1024px / mobile; keyboard-navigable; semantic HTML.

## 6. Success criteria
See `docs/IMPLEMENTATION_PLAN.md` §Acceptance Criteria — restated from the
brief, each one mapped to a phase and a concrete check (migration, test, or
manual script).
