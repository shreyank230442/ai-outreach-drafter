from data.database import get_db

db = get_db()
cursor = db.cursor()

cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table'
""")

tables = cursor.fetchall()

print("📦 Tables in database:")
for table in tables:
    print("-", table["name"])
