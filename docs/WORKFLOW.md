# Workflow engine

The backend enforces these transitions: `pending → assigned → in_progress → approved → completed`; `in_progress → rejected` is also valid. Requesters cancel pending requests through the dedicated cancellation endpoint.

Only managers or administrators assign, approve, or reject. The assignee (or manager/admin) can start and complete work. Every assignment is recorded in `request_assignments`; every accepted state transition is appended to `request_status_history`.

Endpoints: `POST /api/v1/requests/{id}/assign`, `POST /api/v1/requests/{id}/transition`, and `GET /api/v1/requests/{id}/history`.
