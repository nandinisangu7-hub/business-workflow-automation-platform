"""
Shared enums for the domain.

DESIGN NOTE — why UserRole is an enum column, not a `roles` table:
With exactly three fixed, code-defined roles (employee/manager/admin) that
never change at runtime, a separate `roles` table would add a join for no
real benefit — it's the kind of "unnecessarily complicated database"
Phase 2's brief explicitly warns against. If this ever needed per-tenant
custom roles or fine-grained permissions assigned dynamically, THAT would
be the moment to extract a `roles` table with a `role_permissions` join
table. Good to say out loud in an interview: this is a deliberate
trade-off, not an oversight.

Valid workflow transitions (e.g. "PENDING can only move to ASSIGNED or
CANCELLED") are intentionally NOT defined here. Enums describe what values
are legal; deciding which transitions between them are legal is business
logic, and belongs in the service layer built in Phase 5.
"""
import enum


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class RequestPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
