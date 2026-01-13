# data/migrate_outreach_table.py

from data.database import get_db


def migrate():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outreach_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            to_email TEXT NOT NULL,
            initial_subject TEXT NOT NULL,
            initial_body TEXT NOT NULL,
            initial_created_at TEXT NOT NULL,

            followup_1_created INTEGER DEFAULT 0,
            followup_2_created INTEGER DEFAULT 0,
            followup_3_created INTEGER DEFAULT 0,

            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.commit()
    print("✅ outreach_emails table ready")


if __name__ == "__main__":
    migrate()
