
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "community.db"

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

existing_columns = {
    row[1]
    for row in cursor.execute(
        "PRAGMA table_info(complaints)"
    ).fetchall()
}

if "latitude" not in existing_columns:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN latitude FLOAT"
    )
    print("Added latitude column.")
else:
    print("Latitude column already exists.")

if "longitude" not in existing_columns:
    cursor.execute(
        "ALTER TABLE complaints ADD COLUMN longitude FLOAT"
    )
    print("Added longitude column.")
else:
    print("Longitude column already exists.")

connection.commit()
connection.close()

print("Location coordinate migration completed.")
