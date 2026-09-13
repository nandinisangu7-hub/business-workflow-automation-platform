# Request management API

All request endpoints require a bearer token. Employees can create, view, edit while pending, cancel while pending, and comment on their own requests. Managers additionally see requests from their direct reports. Administrators can view every request and create categories.

## Endpoints

- `GET /api/v1/categories` and `POST /api/v1/categories` (admin for creation)
- `GET /api/v1/requests`, `POST /api/v1/requests`
- `GET /api/v1/requests/{request_id}`, `PATCH /api/v1/requests/{request_id}`
- `POST /api/v1/requests/{request_id}/cancel`
- `GET` and `POST /api/v1/requests/{request_id}/comments`

Request creation validates title, description, priority, due date, and category availability. The Phase 5 workflow engine will add assignment and controlled non-cancellation status transitions.
