
import sqlite3

DB_PATH = "community.db"

new_columns = {
    "title": "VARCHAR(200)",
    "predicted_category": "VARCHAR(100)",
    "prediction_confidence": "FLOAT",
    "ward": "VARCHAR(100)",
    "incident_datetime": "DATETIME",
    "photo_filename": "VARCHAR(255)",
    "user_id": "INTEGER"
}

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("PRAGMA table_info(complaints)")
existing_columns = [column[1] for column in cursor.fetchall()]

for column_name, column_type in new_columns.items():
    if column_name not in existing_columns:
        cursor.execute(
            f"ALTER TABLE complaints ADD COLUMN {column_name} {column_type}"
        )
        print(f"Added column: {column_name}")
    else:
        print(f"Already exists: {column_name}")

connection.commit()
connection.close()

print("Database migration completed.")
