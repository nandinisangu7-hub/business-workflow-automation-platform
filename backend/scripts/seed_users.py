"""Create a small local demonstration hierarchy after migrations have run."""
import os

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import UserRole
from app.models.user import User


def main() -> None:
    password = os.getenv("SEED_PASSWORD")
    if not password or len(password) < 8:
        raise SystemExit("Set SEED_PASSWORD to a password of at least 8 characters; no default credentials are provided.")
    db = SessionLocal()
    try:
        accounts = {"admin@example.local": ("Platform Administrator", UserRole.ADMIN), "manager@example.local": ("Operations Manager", UserRole.MANAGER), "employee@example.local": ("Demo Employee", UserRole.EMPLOYEE)}
        users: dict[str, User] = {}
        for email, (full_name, role) in accounts.items():
            user = db.query(User).filter_by(email=email).one_or_none()
            if user is None:
                user = User(email=email, full_name=full_name, role=role, hashed_password=hash_password(password))
                db.add(user)
                db.flush()
            users[email] = user
        users["employee@example.local"].manager_id = users["manager@example.local"].id
        db.commit()
        print("Seed users are ready. Re-running does not replace existing passwords.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
