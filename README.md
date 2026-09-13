# Business Workflow Automation Platform

An enterprise-style workflow automation platform built to demonstrate
full-stack application engineering practices.

> **Status: Phase 2 of 14 complete.** This README is intentionally partial
> right now — it will be filled out section by section as each phase lands,
> and rewritten properly in Phase 14. See [Development Phases](#development-phases)
> below for what exists today versus what's planned.

## Overview

Employees submit business requests (IT equipment, software access, leave,
expense reimbursement, purchase requests, general service requests) through
a controlled workflow instead of email or spreadsheets:

```
Create Request → Pending → Assigned → In Progress → Approved / Rejected → Completed
```

Every transition is validated against an explicit state machine, recorded
in an append-only audit log, and triggers an in-app notification to the
relevant party.

## Architecture

```
                    React + TypeScript
                           │
                           │ HTTPS / JSON
                           ↓
                    FastAPI REST API
                           │
             ┌─────────────┼──────────────┐
             ↓             ↓              ↓
       Authentication   Services      Integrations
       & Authorization      │          (External API)
                            ↓
                       Repositories
                            │
                            ↓
                       PostgreSQL
                       /        \
                      ↓          ↓
                 Audit Logs   Notifications
```

**Layering rules this project follows:**
- Routes parse HTTP and call exactly one service method — no business logic in route handlers.
- Services own business rules (e.g. valid workflow transitions) and know nothing about HTTP.
- Repositories are the only layer allowed to write SQLAlchemy queries.
- Integrations isolate all external-API calls behind a stable interface.

## Technology Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React + TypeScript + Vite | Typed API contracts, fast dev loop |
| Backend | FastAPI + Pydantic | Async-capable, free OpenAPI docs, first-class validation |
| Database | PostgreSQL + SQLAlchemy + Alembic | Relational integrity for workflow state; versioned schema migrations |
| Auth | JWT (python-jose) + passlib (bcrypt) | Stateless auth suited to a decoupled SPA + API |
| Testing | Pytest / HTTPX (backend), Vitest / React Testing Library (frontend) | |
| DevOps | Docker, Docker Compose, GitHub Actions | Reproducible local + CI environment |

Full rationale for each choice is in `INTERVIEW.md` (added in Phase 14).

## Project Structure

```
business-workflow-automation-platform/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, health check
│   │   ├── api/v1/             # route modules (Phase 3+)
│   │   ├── core/                # config.py (done), security.py (Phase 3)
│   │   ├── db/                  # base.py, session.py (done)
│   │   ├── models/               # SQLAlchemy models (Phase 2)
│   │   ├── schemas/               # Pydantic schemas (Phase 2+)
│   │   ├── services/               # business logic (Phase 4+)
│   │   ├── repositories/            # data access (Phase 2+)
│   │   ├── integrations/             # external API client (Phase 8)
│   │   └── utils/
│   ├── alembic/                        # migrations (Phase 2)
│   ├── tests/{unit,integration}/
│   ├── requirements.txt
│   └── Dockerfile                      # (Phase 12)
├── frontend/
│   ├── src/{components,pages,layouts,api,hooks,types,utils,context,routes}/
│   ├── tests/
│   ├── package.json
│   └── Dockerfile                      # (Phase 12)
├── docs/                                # API.md, ARCHITECTURE.md, DATABASE.md, WORKFLOW.md (Phase 14)
├── .github/workflows/                   # CI (Phase 13)
├── docker-compose.yml                   # (Phase 12)
└── .env.example
```

## Database Design (Phase 2)

8 tables, normalized, UUID primary keys, no unnecessary complexity (3
fixed user roles are an enum column, not a `roles` table — see
`app/models/enums.py` for the reasoning):

```
users ──┬─< requests >──┬── request_categories
         (requester_id) │  (category_id)
         (assignee_id)  │
         (manager_id,   │
          self-ref)     │
                        ├─< request_assignments
                        ├─< request_comments
                        └─< request_status_history

users ──< notifications
users ──< audit_logs   (entity_id is a plain string, not an FK — see
                         app/models/audit_log.py for why)
```

Full ER diagram and column-level rationale will move to `docs/DATABASE.md`
in Phase 14.

## Running Locally

**Database migrations** (run once, after setting `DATABASE_URL` in your
`.env` — see `.env.example`; requires a running Postgres, which arrives in
Phase 12's Docker Compose — until then, migrations can also be verified
against a local SQLite file for development, as shown in Phase 2's tests):
```bash
cd backend
PYTHONPATH=. alembic upgrade head
```

**Backend:**
```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```
Visit `http://localhost:8000/health` and `http://localhost:8000/docs`.

**Backend tests:**
```bash
cd backend
PYTHONPATH=. pytest
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:5173` — it should show the health check succeeding
against the backend (start the backend first).

**Frontend tests:**
```bash
cd frontend
npm run test
```

## Development Phases

- [x] **Phase 1** — Architecture, repository structure, backend/frontend skeleton that boots and is tested
- [x] **Phase 2** — Database models and Alembic migrations
- [ ] Phase 3 — Authentication and authorization (+ seed data, deferred from Phase 2 since it needs password hashing)
- [ ] Phase 4 — Request management APIs
- [ ] Phase 5 — Workflow engine
- [ ] Phase 6 — Audit logging
- [ ] Phase 7 — Notifications
- [ ] Phase 8 — External API integration
- [ ] Phase 9 — React frontend (pages, components)
- [ ] Phase 10 — Search / filter / pagination
- [ ] Phase 11 — Testing (deepening coverage across phases 2–9)
- [ ] Phase 12 — Docker
- [ ] Phase 13 — GitHub Actions CI
- [ ] Phase 14 — Documentation and final README

## Future Improvements

To be documented in Phase 14, alongside honest, non-fabricated notes on
current limitations (e.g. JWT has no server-side revocation without an
added blocklist).
