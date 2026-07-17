import argparse

from sqlalchemy import select

from src.db.base import SessionLocal
from src.modules.admin_auth.models import AdminRole, AdminUser
from src.modules.admin_auth.security import hash_password


def seed_admin(email: str, password: str) -> None:
    """Create or update a SUPER_ADMIN. This is the only way to mint a SUPER_ADMIN —
    the UI's Create Admin always creates role=ADMIN."""
    db = SessionLocal()
    try:
        admin = db.scalar(select(AdminUser).where(AdminUser.email == email))
        if admin is None:
            admin = AdminUser(
                email=email,
                password_hash=hash_password(password),
                role=AdminRole.SUPER_ADMIN,
                is_active=True,
            )
            db.add(admin)
            action = "Created"
        else:
            admin.password_hash = hash_password(password)
            admin.role = AdminRole.SUPER_ADMIN
            admin.is_active = True
            action = "Updated"
        db.commit()
        print(f"{action} SUPER_ADMIN user: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update a seeded admin user.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    seed_admin(args.email, args.password)
