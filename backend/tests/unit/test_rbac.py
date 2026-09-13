import pytest
from fastapi import HTTPException

from app.api.v1.dependencies import require_roles
from app.models.enums import UserRole
from app.models.user import User


def user(role: UserRole) -> User:
    return User(email=f"{role.value}@example.com", full_name=role.value, hashed_password="hash", role=role)


def test_role_guard_allows_manager_and_admin_but_not_employee():
    guard = require_roles(UserRole.MANAGER, UserRole.ADMIN)
    assert guard(user(UserRole.MANAGER)).role == UserRole.MANAGER
    assert guard(user(UserRole.ADMIN)).role == UserRole.ADMIN
    with pytest.raises(HTTPException) as error:
        guard(user(UserRole.EMPLOYEE))
    assert error.value.status_code == 403
