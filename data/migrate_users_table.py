# data/migrate_users_table.py

from data.database import get_db


def migrate():
    db = get_db()
    cursor = db.cursor()

    # Add is_verified column
    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0"
        )
    except Exception:
        pass  # column already exists

    # Add otp_code column
    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN otp_code TEXT"
        )
    except Exception:
        pass

    # Add otp_expires_at column
    try:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN otp_expires_at TEXT"
        )
    except Exception:
        pass

    db.commit()
    print("✅ Users table migrated successfully")


if __name__ == "__main__":
    migrate()
