# Business Workflow Automation Platform

A full-stack enterprise-style workflow management application designed to demonstrate real-world software engineering practices including authentication, role-based authorization, workflow automation, REST APIs, database management, audit logging, testing, Docker, and CI/CD.

## Project Status

**Completed**

The application includes backend APIs, a React frontend, PostgreSQL support, automated testing, Docker deployment, and GitHub Actions CI.

---

## Key Features

- User authentication
- JWT-based authorization
- Role-Based Access Control (RBAC)
- Employee, Manager, and Admin roles
- Business request management
- Request workflow and state transitions
- Request assignment
- Search and filtering
- Pagination
- Dashboard summary
- User management
- Audit logging
- Notifications
- External API integration
- Input validation
- Error handling
- REST API
- API documentation
- Unit tests
- Integration tests
- Frontend tests
- Docker and Docker Compose
- GitHub Actions CI

---

## Workflow

A typical request follows this lifecycle:

```text
Pending
   ↓
Assigned
   ↓
In Progress
   ↓
Approved / Rejected
   ↓
Completed