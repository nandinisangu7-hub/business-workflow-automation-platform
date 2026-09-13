\# Database Documentation



\## 1. Overview



The Business Workflow Automation Platform uses a relational database for persistent application data.



Primary database:



\*\*PostgreSQL\*\*



The backend uses:



\- SQLAlchemy for ORM and database access

\- Alembic for database migrations

\- PostgreSQL for the application database

\- SQLite in-memory databases for isolated automated tests



\## 2. Database Architecture



```text

FastAPI

&#x20;  ↓

Service Layer

&#x20;  ↓

Repository / Data Access

&#x20;  ↓

SQLAlchemy ORM

&#x20;  ↓

PostgreSQL

