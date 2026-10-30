# AICTE CaseWatch
### Integrated Dashboard for Monitoring and Tracking Institution-Related Complaint Cases Across AICTE Bureaus/Cells

**Smart India Hackathon (SIH) 2026 | Problem Statement ID: 26264**

AICTE CaseWatch is an integrated institution complaint monitoring and tracking platform designed to provide a centralized, real-time view of institution-related complaints and grievance cases across different AICTE Bureaus and Cells, including the Regulation Bureau (RB), Public Grievance Redressal Cell (PGRC), Regional Bureaus, and other configured departments.

The platform addresses the challenges of fragmented complaint management, overlapping institutional cases, duplicated actions, delayed resolution, and limited coordination between different Bureaus/Cells.

It provides authorized AICTE officials with a unified dashboard to monitor complaint lifecycles, identify institutions with multiple active cases, coordinate cross-bureau actions, track Service Level Agreement (SLA) compliance, and maintain a complete, auditable history of every action.

**AICTE CaseWatch establishes a single source of truth for institution-related complaints and regulatory actions.**

---

## Problem Statement

**Organization:** All India Council for Technical Education (AICTE)  
**Department:** Regulation Bureau  
**Category:** Software  
**Problem Statement ID:** 26264

AICTE receives complaints and grievances from students, faculty members, stakeholders, and other concerned parties regarding technical education institutions.

These complaints are processed by multiple Bureaus and Cells, including RB and PGRC. However, the absence of a centralized monitoring mechanism creates several challenges:

- Multiple Bureaus/Cells may independently process complaints concerning the same institution.
- Duplicate or overlapping actions may occur without the knowledge of other departments.
- Tracking the complete history and movement of complaints becomes difficult.
- Identifying the Bureau/Cell currently responsible for a case is challenging.
- Delays in complaint disposal and SLA violations may go unnoticed.
- Management lacks a consolidated view of institutional complaints and departmental workloads.

AICTE CaseWatch addresses these challenges through a unified complaint monitoring, coordination, and workflow management platform.

---

## Key Features

### 1. Centralized Institution Profile

- Maintain a consolidated profile for every technical education institution.
- Identify institutions using their unique AICTE Permanent ID.
- Store institution name, address, region, and other relevant details.
- View the complete complaint history associated with an institution.
- Access cases handled by different Bureaus/Cells from a single profile.

### 2. Comprehensive Complaint Tracking

- Generate and track unique Complaint/Case IDs.
- Record complaint receipt dates and categories.
- Monitor current complaint status and assigned Bureau/Cell.
- Track the responsible officer and latest action taken.
- Maintain next-action requirements and expected disposal dates.
- Support complaint lifecycle management from registration to disposal.

### 3. Cross-Bureau Overlap and Duplicate Detection

- Automatically identify multiple active complaints associated with the same institution.
- Detect potential overlaps between RB, PGRC, and other configured Bureaus/Cells.
- Generate alerts when multiple departments handle complaints concerning the same institution.
- Identify potential duplicate complaints for authorized review.
- Link related complaints and maintain coordination history.
- Support confirmation and dismissal of potential duplicate alerts.

**Example:**

An institution receives two separate complaints:

| Bureau/Cell | Complaint | Status |
|---|---|---|
| PGRC | Complaint A | Under Process |
| Regulation Bureau | Complaint B | Under Process |

CaseWatch identifies the common institution and generates:

**Potential Overlapping Cases – Coordination Required**

This helps officials coordinate their actions and avoid conflicting or duplicated efforts.

### 4. Real-Time Monitoring Dashboard

Provides a consolidated view of complaint management across AICTE Bureaus/Cells.

Dashboard indicators include:

- Total complaints received.
- Pending complaints.
- Complaints under process.
- Disposed complaints.
- Transferred complaints.
- Escalated complaints.
- Overdue cases and SLA violations.
- Bureau-wise and region-wise workload.
- Institution-wise complaint status.
- Complaint trends and disposal performance.

All dashboard metrics are retrieved through live database queries.

### 5. Complaint Workflow and Action Management

- Manage complaint assignments to authorized officers.
- Support complaint status transitions.
- Transfer cases between Bureaus/Cells.
- Escalate cases requiring higher-level intervention.
- Dispose of complaints through controlled workflows.
- Maintain chronological action history.
- Record officer details, timestamps, remarks, and supporting documents.
- Preserve an audit trail of complaint-related activities.

### 6. Advanced Search and Filtering

Authorized users can search and filter complaints using:

- Institution Name.
- AICTE Permanent ID.
- Complaint/Case ID.
- Bureau/Cell.
- Region.
- Complaint Category.
- Complaint Status.
- Date Range.

### 7. Alerts and Notifications

- Potential duplicate and overlapping complaint alerts.
- Cross-bureau coordination alerts.
- Complaint assignment notifications.
- Case transfer notifications.
- Escalation notifications.
- SLA compliance monitoring.
- Overdue complaint identification.

Notifications are available within the application.

### 8. Reports and Analytics

Enable officials and management to monitor complaint performance through:

- Bureau-wise complaint reports.
- Region-wise complaint reports.
- Institution-wise complaint history.
- Status-wise complaint distribution.
- Pending case ageing analysis.
- Complaint disposal statistics.
- Overlapping and duplicate case reports.
- CSV complaint export.

---

## Innovation and Technical Approach

AICTE CaseWatch combines centralized institution identification, rule-based overlap detection, controlled complaint workflows, and real-time analytics.

The system uses institution-level associations to identify complaints being handled by multiple Bureaus/Cells, even when the complaints have different references or descriptions.

Its key capabilities include:

- Institution-centric complaint aggregation.
- Cross-bureau overlap detection.
- Potential duplicate identification and review.
- Role-based workflow authorization.
- SLA and overdue case monitoring.
- Immutable audit history.
- Centralized management analytics.

The platform is designed to reduce manual coordination, improve institutional complaint visibility, and support data-driven decision-making by AICTE officials.

---

## User Roles and Access Control

The platform supports role-based access control (RBAC) to ensure that users can perform only the actions authorized for their responsibilities.

| Role | Responsibility |
|---|---|
| System Administrator | System configuration and user management |
| Senior Management | Overall monitoring and management insights |
| Bureau Officer | Complaint processing and bureau-level operations |
| Regional Officer | Regional complaint monitoring |
| Auditor | Read-only access to records and audit history |

Authorization is enforced by the backend rather than relying solely on frontend visibility.

---

## Technology Stack

### Frontend
- Next.js 16 (App Router)
- React 19
- TypeScript (Strict Mode)
- Tailwind CSS v4
- shadcn/ui
- TanStack Table v8
- Recharts
- React Hook Form
- Zod

### Backend
- Python
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- Alembic

### Database
- PostgreSQL 16

### Authentication and Security
- Server-side session authentication using HttpOnly cookies.
- Double-submit CSRF protection.
- Argon2 password hashing.
- Backend-enforced Role-Based Access Control (RBAC).

### Infrastructure and Development
- Docker
- Docker Compose
- Git and GitHub
- Pytest
- Ruff
- Black
- Mypy
- Vitest
- Playwright

---

## System Architecture

The application follows a modular full-stack architecture.

```text
                  AICTE CASEWATCH
                         |
              Next.js Frontend
                 (React + TS)
                         |
                  API Integration
                         |
                  FastAPI Backend
                         |
          +--------------+--------------+
          |              |              |
       Services     Repositories      Auth/RBAC
          |              |              |
          +--------------+--------------+
                         |
                   PostgreSQL
                         |
             Complaint & Audit Data
```

### Project Structure

```text
casesync-1/
│
├── apps/
│   ├── web/                     # Next.js frontend
│   │   └── src/
│   │       ├── app/             # Application routes
│   │       ├── features/        # Feature modules
│   │       ├── components/      # Shared UI components
│   │       └── lib/             # API clients and utilities
│   │
│   └── api/                     # FastAPI backend
│       ├── app/
│       │   ├── api/v1/
│       │   │   └── endpoints/   # API routes
│       │   ├── services/        # Business logic
│       │   ├── repositories/    # Database queries
│       │   ├── models/          # SQLAlchemy models
│       │   └── schemas/         # Pydantic schemas
│       │
│       └── scripts/
│           └── seed.py          # Demo data generation
│
├── infrastructure/
│   └── docker/                  # Docker configurations
│
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── API_SPEC.md
│   └── IMPLEMENTATION_PLAN.md
│
├── .env.example
├── docker-compose.yml
├── CLAUDE.md
└── README.md
```

---

## Getting Started

### Prerequisites

Install the following tools:

- Git
- Docker Desktop
- Visual Studio Code
- Node.js (for local frontend development)
- Python (for local backend development)

### Option A: Run Using Docker Compose (Recommended)

**1. Clone the repository**

```bash
git clone https://github.com/Bs-Gokulnath/casesync-1.git
cd casesync-1
```

**2. Configure environment variables**

```bash
cp .env.example .env
```

Configure the required environment variables in the `.env` file.

**3. Build and start the application**

```bash
docker compose up -d --build
```

**4. Generate fictional demo data**

```bash
docker compose exec api python -m scripts.seed
```

**5. Access the application**

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/api/v1/docs |

### Option B: Run Services Individually

**1. Start PostgreSQL**

```bash
docker compose up -d postgres
```

**2. Set up the backend**

```bash
cd apps/api

python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

Run database migrations:

```bash
alembic upgrade head
```

Seed demo data:

```bash
python -m scripts.seed
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

**3. Set up the frontend**

Open a separate terminal:

```bash
cd apps/web
npm install
npm run dev
```

Access the application at http://localhost:3000.

---

## Demo Credentials

The application provides fictional demo accounts for testing different user roles.

All seeded accounts share the password:

```text
Demo@12345
```

| Email | Role |
|---|---|
| admin@aictecasewatch-demo.org | System Administrator |
| management@aictecasewatch-demo.org | Senior Management |
| rb.officer@aictecasewatch-demo.org | Bureau Officer – Regional Bureau (Delhi) |
| pgrc.officer@aictecasewatch-demo.org | Bureau Officer – PGRC |
| regional.officer@aictecasewatch-demo.org | Regional Officer – Northern Region |
| auditor@aictecasewatch-demo.org | Auditor (Read Only) |

**Note:** These accounts and all seeded institutional and complaint records are fictional and intended exclusively for local development and demonstration.

---

## Testing and Quality Assurance

### Backend Testing

Run from `apps/api` with the virtual environment activated and PostgreSQL available.

```bash
pytest
```

The project includes 63 backend unit and integration tests.

Code quality checks:

```bash
ruff check .
black --check .
mypy app
```

### Frontend Testing

Run from `apps/web`.

```bash
npm run typecheck
npm run lint
npm run test
npm run build
```

### End-to-End Testing

With the complete Docker Compose stack running and demo data seeded:

```bash
npm run test:e2e
```

Playwright tests cover key application workflows, including login, complaint creation, case transfer, overlap review, and complaint disposal.

### Implementation Verification

The implementation has been smoke-tested across the Docker Compose stack, including:

- Role-based application access.
- Backend API communication.
- Complaint creation and workflow operations.
- Cross-bureau overlap scenarios.
- Multipart document upload and download.
- CSRF-protected backend mutations.
- Database-backed dashboard metrics.

Refer to `docs/IMPLEMENTATION_PLAN.md` for the implementation and verification details.

---

## Known Limitations and Future Enhancements

The current implementation provides the core complaint monitoring and workflow capabilities. The following enhancements remain potential future improvements:

- **Email/SMS Notifications:** Current notifications are in-app only. External email and SMS delivery are not implemented.
- **Scheduled SLA Notifications:** Approaching-deadline and overdue cases are computed dynamically in the Work Queue. A background scheduler using Celery or APScheduler could enable persistent reminders.
- **Advanced Report Export:** CSV export currently supports complaints only. Multi-sheet reporting and advanced PDF exports could be added.
- **Fine-Grained Resource Authorization:** Individual complaint and institution reads and workflow actions are not yet fully bureau/region-scoped. Additional resource-level authorization is required.
- **Expanded E2E Coverage:** Existing Playwright tests cover the primary workflows but are not an exhaustive UI regression suite.
- **AI-Assisted Complaint Matching:** Semantic similarity analysis could further improve identification of related complaints when institution references or complaint descriptions differ.

---

## Expected Impact

AICTE CaseWatch aims to improve the efficiency, transparency, and accountability of institution-related complaint management.

| Challenge | Expected Improvement |
|---|---|
| Fragmented complaint records | Centralized institution complaint history |
| Duplicate departmental actions | Cross-bureau overlap detection |
| Delayed complaint disposal | SLA monitoring and overdue identification |
| Poor interdepartmental coordination | Shared case visibility and workflow tracking |
| Limited management visibility | Real-time dashboards and analytics |
| Lack of accountability | Chronological and auditable action history |

### Expected Outcomes

- Reduced duplication of work across Bureaus/Cells.
- Improved coordination between RB, PGRC, and other departments.
- Better visibility into institution-related complaints.
- Timely monitoring and disposal of pending cases.
- Improved accountability and transparency.
- Data-driven decision-making for AICTE management.

---

## Documentation

For detailed technical and functional documentation, refer to:

- `docs/PRD.md` – Product Requirements Document.
- `docs/ARCHITECTURE.md` – System Architecture.
- `docs/DATABASE.md` – Database Design.
- `docs/API_SPEC.md` – API Specifications.
- `docs/IMPLEMENTATION_PLAN.md` – Implementation and Verification Log.
- `CLAUDE.md` – Architecture Rules and Development Guidelines.

---

**AICTE CaseWatch – One Institution. One Consolidated View. Better Coordination.**

*Developed to address Smart India Hackathon 2026 Problem Statement 26264.*
