# data/init_db.py

from data.database import get_db


def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            otp_code TEXT,
            otp_expires_at TEXT
        )
    """)

    db.commit()
    print("✅ Database initialized successfully")


if __name__ == "__main__":
    init_db()