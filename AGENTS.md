# AGENTS.md

## Project

Business Workflow Automation Platform

This is a portfolio-grade, enterprise-style full-stack application designed to demonstrate strong software/application engineering skills.

The application automates internal business requests through a controlled workflow.

Primary workflow:

Employee creates request
        ↓
Pending
        ↓
Assigned
        ↓
In Progress
        ↓
Approved / Rejected
        ↓
Completed

The project must remain understandable and explainable by a final-year B.Tech student.

---

# 1. PRIMARY OBJECTIVE

Build a complete, working, maintainable full-stack business workflow application.

The project must demonstrate:

- Python
- FastAPI
- REST APIs
- React
- TypeScript
- PostgreSQL
- SQLAlchemy
- Alembic
- Authentication
- JWT
- Role-Based Access Control
- Input validation
- Business logic
- Search
- Filtering
- Pagination
- Audit logging
- Notifications
- External API integration
- Unit testing
- Integration testing
- Docker
- Docker Compose
- GitHub Actions
- API documentation
- Clean architecture
- Error handling
- Logging

The application must work end-to-end.

Do not build a collection of disconnected demos.

---

# 2. IMPORTANT EXISTING PROJECT STATE

Before changing anything:

INSPECT THE ACTUAL REPOSITORY.

Do not assume the repository exactly matches this document.

The project is expected to already contain Phase 1 and Phase 2 work, including some or all of:

- FastAPI backend
- React frontend skeleton
- SQLAlchemy models
- PostgreSQL configuration
- Alembic
- User model
- Request model
- RequestCategory
- RequestAssignment
- RequestComment
- RequestStatusHistory
- Notification
- AuditLog
- UserRole
- RequestStatus
- RequestPriority
- database session
- initial migrations
- tests

Preserve working existing functionality.

Never rebuild an already completed phase merely for stylistic reasons.

---

# 3. DEVELOPMENT PHASES

The remaining project should be implemented in this order.

Phase 1:
Project architecture and initial setup

Phase 2:
Database models and migrations

Phase 3:
Authentication and authorization

Phase 4:
Request management APIs

Phase 5:
Workflow engine

Phase 6:
Audit logging

Phase 7:
Notifications

Phase 8:
External API integration

Phase 9:
React frontend

Phase 10:
Search, filtering, sorting and pagination

Phase 11:
Comprehensive testing

Phase 12:
Docker and Docker Compose

Phase 13:
GitHub Actions CI

Phase 14:
Final documentation, security review and portfolio polish

If a phase is already complete, verify it rather than rebuilding it.

---

# 4. PHASE EXECUTION RULE

Work sequentially.

Do not skip phases.

For every phase:

1. Inspect existing implementation.
2. Identify missing functionality.
3. Plan the change.
4. Implement the change.
5. Run appropriate tests.
6. Fix failures.
7. Run relevant regression tests.
8. Review the implementation.
9. Update documentation.
10. Commit the phase only after verification succeeds.

Do not move to the next phase while the current phase has unresolved test failures unless the failure is clearly unrelated and documented.

---

# 5. AUTONOMY

The agent should work autonomously.

Do not repeatedly ask for confirmation for ordinary implementation decisions.

Make reasonable engineering decisions based on:

1. Existing repository architecture
2. Existing code
3. This AGENTS.md
4. The master user prompt
5. Standard engineering practices

Ask for user input only when continuing would require a genuinely important decision that cannot safely be inferred.

Examples:

- destructive database operation
- deleting user data
- replacing the existing architecture
- changing the core technology stack
- pushing to a different GitHub repository
- changing production credentials
- an unresolved security issue requiring human approval

Do not stop merely because a small implementation detail is unspecified.

---

# 6. NEVER GUESS THE CODEBASE

If the repository contains relevant code:

READ IT.

Do not invent:

- filenames
- functions
- classes
- database fields
- routes
- dependencies
- existing tests
- migration versions

If unsure, inspect the repository.

Never claim something exists unless it has been verified.

---

# 7. TECHNOLOGY STACK

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT authentication
- secure password hashing

## Frontend

- React
- TypeScript
- Vite
- React Router
- Axios or the existing HTTP client
- responsive UI

## Testing

Backend:

- pytest
- FastAPI TestClient or HTTPX

Frontend:

- Vitest
- React Testing Library where appropriate

## DevOps

- Docker
- Docker Compose
- GitHub Actions

Use existing dependencies where possible.

Do not add dependencies without a real reason.

---

# 8. ARCHITECTURE

Backend architecture should generally follow:

API Routes
    ↓
Services / Business Logic
    ↓
Repositories / Data Access
    ↓
SQLAlchemy
    ↓
PostgreSQL

Keep responsibilities separated.

API routes should not contain large amounts of business logic.

Business rules belong in services.

Database access belongs in repositories where that pattern is already established.

---

# 9. AUTHENTICATION

Implement:

- registration
- login
- JWT access tokens
- password hashing
- current-user endpoint
- protected endpoints
- token validation
- token expiration
- inactive-user checks

Never store plaintext passwords.

Never return password hashes.

Never put passwords into JWTs.

Never hardcode production secrets.

---

# 10. AUTHORIZATION

Roles:

- EMPLOYEE
- MANAGER
- ADMIN

Implement backend RBAC.

Example:

Employee:
- create requests
- view permitted requests
- comment
- view notifications

Manager:
- employee permissions
- view assigned/team requests
- assign requests
- approve/reject requests

Admin:
- full administrative access
- user management
- audit logs
- categories
- system-level dashboard

Frontend hiding is NOT security.

Every sensitive action must be checked by the backend.

---

# 11. DATABASE

Use PostgreSQL for the application.

Expected entities include:

- users
- roles or role representation already established by the project
- requests
- request_categories
- request_assignments
- request_comments
- request_status_history
- notifications
- audit_logs

Preserve existing schema decisions unless a real defect requires modification.

Use:

- primary keys
- foreign keys
- constraints
- indexes
- timestamps
- appropriate relationships

Avoid unnecessary database complexity.

---

# 12. REQUEST WORKFLOW

Valid request statuses:

- PENDING
- ASSIGNED
- IN_PROGRESS
- APPROVED
- REJECTED
- COMPLETED
- CANCELLED

Do not allow arbitrary state changes.

Example:

PENDING
→ ASSIGNED
→ IN_PROGRESS
→ APPROVED
→ COMPLETED

Possible rejection:

IN_PROGRESS
→ REJECTED

Possible cancellation:

PENDING
→ CANCELLED

Business rules must be enforced on the backend.

Every important state transition should eventually be auditable.

---

# 13. REQUEST FEATURES

Implement:

- create request
- retrieve request
- update request where permitted
- cancel request where permitted
- assign request
- approve request
- reject request
- complete request
- comments
- request history

Support:

- search
- filters
- pagination
- priority
- category
- creator
- assignee
- date ranges

Use server-side search/filtering/pagination.

Do not retrieve the entire database and perform all filtering in React.

---

# 14. AUDIT LOGGING

Audit important business operations.

Examples:

- login
- request created
- request assigned
- status changed
- request approved
- request rejected
- request completed
- request cancelled
- user created
- role changed

Audit records should include useful context such as:

- actor
- action
- entity
- entity ID
- timestamp
- relevant metadata

Do not expose sensitive secrets in logs.

Do not allow normal users to edit historical audit records.

---

# 15. NOTIFICATIONS

Implement internal notifications.

Examples:

Request created:
→ manager notification

Request assigned:
→ employee notification

Request approved/rejected:
→ employee notification

Request completed:
→ employee notification

Notification should support:

- recipient
- title
- message
- type
- read/unread
- timestamp

An external email provider is optional.

Do not add unnecessary external notification infrastructure.

---

# 16. EXTERNAL API INTEGRATION

Implement one meaningful external integration.

The integration must demonstrate:

- HTTP request
- authentication/configuration if required
- response validation
- transformation
- timeout handling
- error handling
- logging

Keep external integration code separate from API route handlers.

Never commit API keys.

If an external service is unreliable or requires credentials, use a clearly documented mock adapter while preserving the same interface.

Do not pretend a mock service is a real production integration.

---

# 17. FRONTEND

Create a professional enterprise dashboard.

Expected pages include:

- Login
- Register
- Dashboard
- Requests
- Create Request
- Request Details
- Notifications
- Profile
- Admin Users
- Admin Audit Logs

Use reusable components.

Avoid duplicated UI logic.

Support:

- loading states
- empty states
- error states
- responsive layout
- accessible controls
- clear navigation

---

# 18. FRONTEND API LAYER

Do not scatter raw HTTP requests throughout components.

Prefer a centralized API layer such as:

src/api/auth.ts
src/api/users.ts
src/api/requests.ts
src/api/notifications.ts
src/api/dashboard.ts

Use TypeScript types for API responses.

Handle authentication state centrally.

---

# 19. ERROR HANDLING

Use meaningful HTTP status codes.

Expected categories include:

400
401
403
404
409
422
500

Do not expose:

- stack traces
- passwords
- secrets
- internal database errors
- JWT secrets

Use consistent error responses.

---

# 20. VALIDATION

Validate data on the backend.

Use Pydantic and database constraints appropriately.

Validate:

- email
- strings
- required fields
- enum values
- dates
- pagination parameters
- IDs
- workflow transitions
- ownership/permissions

Frontend validation is helpful for UX but never replaces backend validation.

---

# 21. TESTING

Tests must verify actual behavior.

Prioritize meaningful tests.

Backend tests should cover:

Authentication
Authorization
Requests
Workflow
Validation
Search
Filtering
Pagination
Notifications
Audit logging
External integration
Error handling

Integration tests should exercise realistic flows.

Example:

Register
→ Login
→ Create request
→ Assign
→ Start work
→ Approve
→ Complete

Also test invalid flows.

Example:

Employee
→ Attempt admin operation
→ 403

Invalid transition
→ reject

Missing resource
→ 404

Do not create fake tests that merely assert trivial implementation details.

---

# 22. TESTING RULE

After code changes:

Run the smallest relevant test set first.

If those pass:

Run broader regression tests when justified.

At the end of each phase:

Run the complete relevant test suite.

Never claim tests passed unless they were actually executed.

Never fabricate coverage percentages.

---

# 23. DATABASE MIGRATIONS

Use Alembic.

Do not generate unnecessary migrations.

Before creating a migration:

1. Inspect current models.
2. Compare schema requirements.
3. Determine whether an actual schema change exists.

If no schema change is required, do not create a migration just for appearance.

---

# 24. DOCKER

Eventually provide:

- backend Dockerfile
- frontend Dockerfile
- docker-compose.yml

Expected services:

- frontend
- backend
- postgres

The application should be runnable with:

docker compose up --build

Do not add Redis, Celery, Kubernetes or microservices unless a real project requirement justifies them.

---

# 25. CI

Create GitHub Actions.

CI should eventually run:

- backend installation
- backend tests
- frontend installation
- frontend tests
- frontend build
- relevant linting/type checks

Do not make CI depend on secrets that are not actually available.

Use service containers or another appropriate approach for PostgreSQL integration tests.

---

# 26. DOCUMENTATION

Maintain:

README.md

and appropriate documentation under:

docs/

Expected documentation:

- architecture
- authentication
- database
- workflow
- API
- testing
- Docker/setup
- interview questions

Documentation must describe the actual implementation.

Never document features that do not exist.

---

# 27. SECURITY

Always check:

- plaintext password storage
- hardcoded secrets
- authorization bypass
- insecure direct object references
- missing ownership checks
- SQL injection
- unsafe external requests
- excessive error details
- sensitive logging
- CORS configuration

Do not claim the project is production-secure.

Describe it as:

"enterprise-style" or "production-oriented"

when appropriate.

---

# 28. CODE QUALITY

Prefer:

- small functions
- clear names
- type hints
- reusable components
- single responsibility
- minimal duplication
- clear module boundaries

Avoid:

- giant files
- giant functions
- unnecessary abstractions
- clever code
- unexplained magic constants
- unnecessary dependencies
- generated boilerplate that adds no value

---

# 29. DO NOT OVERENGINEER

Do not introduce technologies simply because they look impressive on a resume.

Do not add:

- Kubernetes
- microservices
- Kafka
- Redis
- Celery
- GraphQL
- event sourcing
- CQRS
- Elasticsearch
- AI/LLM features

unless the actual project requirements justify them.

A smaller working system is better than a complicated broken system.

---

# 30. GIT RULES

Git history should reflect genuine development.

Recommended pattern:

feat(auth): implement authentication
test(auth): add authentication tests
feat(requests): implement request APIs
feat(workflow): implement workflow transitions
feat(audit): add audit logging
feat(notifications): add notifications
feat(integration): add external API integration
feat(frontend): implement dashboard
feat(search): add filtering and pagination
test: expand integration coverage
build: add Docker Compose
ci: add GitHub Actions
docs: finalize project documentation

Do not fabricate historical commits.

Do not rewrite history unnecessarily.

Do not force-push.

Do not delete branches or tags unless explicitly requested.

---

# 31. COMMIT RULE

Only commit after:

- implementation is complete for the phase
- relevant tests pass
- regressions are checked
- no obvious security issue remains
- documentation is updated

Before committing:

Run:

git status
git diff
git diff --check

Review the changes.

Do not commit:

- .env
- secrets
- credentials
- node_modules
- virtual environments
- build artifacts
- database dumps
- IDE-specific junk

Ensure .gitignore is correct.

---

# 32. GITHUB PUSH RULE

A local commit and a GitHub push are different operations.

Only push when:

- the Git remote has been inspected
- it points to the intended repository
- authentication is available
- tests have passed
- the user has authorized the push through the configured environment

Never push to an unknown repository.

Before the first push, verify:

git remote -v

If the remote is missing or ambiguous, stop and ask.

Never expose credentials in output.

---

# 33. DO NOT FABRICATE RESULTS

Never say:

"Tests passed"

unless tests were actually run.

Never say:

"Docker works"

unless Docker was actually tested.

Never say:

"CI passed"

unless CI actually ran.

Never claim:

- performance metrics
- security certifications
- production users
- deployment statistics
- business impact
- uptime
- scalability numbers

unless verified.

---

# 34. USER LEARNING REQUIREMENT

The project must remain understandable to the user.

For every major architectural feature, maintain documentation explaining:

- What it does
- Why it exists
- How it works
- Which files implement it
- How to test it
- What an interviewer may ask

The user should be able to explain the system in an interview.

---

# 35. PHASE COMPLETION REPORT

At the end of every phase, report:

## Phase
Name and number

## Implemented
Concise list

## Files Added
Actual files

## Files Modified
Actual files

## Tests
Actual commands and results

## Verification
What was verified

## Known Issues
Only real issues

## Commit
Actual commit hash if committed

## Next Phase
What comes next

Do not claim completion if verification failed.

---

# 36. FAILURE RECOVERY

If something fails:

1. Read the actual error.
2. Identify the root cause.
3. Make the smallest appropriate fix.
4. Re-run the failing test.
5. Run regression tests.
6. Continue.

Do not randomly rewrite working code.

Do not suppress failures.

Do not weaken tests just to make them pass.

Do not delete a failing test unless the requirement itself changed and the reason is documented.

---

# 37. DESTRUCTIVE OPERATIONS

Never automatically:

- delete the repository
- delete migrations
- reset the database destructively
- drop production databases
- remove user data
- force-push
- overwrite unrelated work
- reset uncommitted user changes

If a destructive action appears necessary, stop and ask.

---

# 38. EXISTING USER CHANGES

Treat uncommitted changes as potentially valuable user work.

Before modifying heavily:

git status

If unrelated uncommitted changes exist:

- preserve them
- do not overwrite them
- do not reset them

Work around them where possible.

---

# 39. FINAL QUALITY BAR

The final repository should be:

- runnable
- tested
- documented
- modular
- understandable
- secure by reasonable development standards
- Dockerized
- CI-ready
- GitHub-ready

The goal is not maximum code volume.

The goal is a strong software engineering project that can be genuinely demonstrated and defended in an interview.

---

# 40. STOP CONDITION

The project is complete only when:

- all required phases are implemented
- application runs
- backend tests pass
- frontend tests pass where applicable
- integration tests pass
- Docker Compose works
- migrations work
- CI configuration is valid
- README is accurate
- architecture documentation is accurate
- no secrets are committed
- Git status is clean except for intentionally ignored files
- final Git commit exists
- GitHub push is completed only if authorized and configured

If GitHub push cannot be completed because authentication is unavailable:

Do not fabricate success.

Report the exact reason and leave the repository with the correct local commits ready to push.

---

# 41. MOST IMPORTANT RULE

DO NOT GENERATE A FAKE ENTERPRISE APPLICATION.

Build a real, working, reasonably scoped application.

Every important feature must actually work.

Every documented feature must actually exist.

Every test result must be real.

Every commit must correspond to actual work.

Every architectural decision should be explainable.

The finished project should look like the work of a strong student software engineer who understands what they built.