import sqlite3
from datetime import datetime

class DatabaseManager:
    """
    Handles local SQLite database operations.
    """

    def __init__(self, db_name="drowsiness.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            ear REAL,
            status TEXT
        )
        """)
        self.conn.commit()

    def insert_record(self, ear, status):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        self.cursor.execute("""
        INSERT INTO alerts(date,time,ear,status)
        VALUES(?,?,?,?)
        """, (date,time,ear,status))

        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM alerts")
        return self.cursor.fetchall()

    def delete_all(self):
        self.cursor.execute("DELETE FROM alerts")
        self.conn.commit()

    def close(self):
        self.conn.close()
