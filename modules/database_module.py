import sqlite3
import os
import threading
from datetime import datetime, timedelta


class DatabaseManager:

    def __init__(self, db_name="drowsiness.db"):
        try:
            from kivy.app import App
            app_dir = App.get_running_app().user_data_dir
        except Exception:
            app_dir = os.getcwd()

        db_path = os.path.join(app_dir, db_name)
        print("DB created at:", db_path)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._lock = threading.Lock()
        self.create_tables()
        self.session_id = None
        self.start_session()

    def create_tables(self):
        with self._lock:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    date TEXT,
                    time TEXT,
                    ear REAL,
                    status TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions(
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT,
                    end_time TEXT,
                    total_alerts INTEGER,
                    avg_ear REAL
                )
            """)
            self.conn.commit()

    def start_session(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._lock:
            self.cursor.execute(
                "INSERT INTO sessions(start_time, end_time, total_alerts, avg_ear) VALUES(?, ?, ?, ?)",
                (now, None, 0, 0)
            )
            self.conn.commit()
            self.session_id = self.cursor.lastrowid
        print(f"Session started: {self.session_id}")

    def end_session(self, avg_ear, total_alerts):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._lock:
            self.cursor.execute(
                "UPDATE sessions SET end_time=?, total_alerts=?, avg_ear=? WHERE session_id=?",
                (now, total_alerts, avg_ear, self.session_id)
            )
            self.conn.commit()
        print("Session ended")

    def insert_record(self, ear, status):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        with self._lock:
            self.cursor.execute(
                "INSERT INTO alerts(session_id, date, time, ear, status) VALUES(?, ?, ?, ?, ?)",
                (self.session_id, date, time_str, ear, status)
            )
            self.conn.commit()

    def get_total_alerts(self):
        with self._lock:
            self.cursor.execute("SELECT COUNT(*) FROM alerts WHERE status='DROWSY'")
            return self.cursor.fetchone()[0]

    def get_average_ear(self):
        with self._lock:
            self.cursor.execute("SELECT AVG(ear) FROM alerts")
            result = self.cursor.fetchone()[0]
        return round(result, 3) if result else 0

    def get_drowsy_percentage(self):
        with self._lock:
            self.cursor.execute("SELECT COUNT(*) FROM alerts")
            total = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM alerts WHERE status='DROWSY'")
            drowsy = self.cursor.fetchone()[0]
        if total == 0:
            return 0
        return round((drowsy / total) * 100, 2)

    def get_last_session(self):
        with self._lock:
            self.cursor.execute(
                "SELECT * FROM sessions ORDER BY session_id DESC LIMIT 1"
            )
            return self.cursor.fetchone()

    def get_filtered_records(self, mode="today"):
        today = datetime.now().strftime("%Y-%m-%d")
        with self._lock:
            if mode == "today":
                self.cursor.execute(
                    "SELECT * FROM alerts WHERE date=? ORDER BY id DESC", (today,)
                )
            elif mode == "yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                self.cursor.execute(
                    "SELECT * FROM alerts WHERE date=? ORDER BY id DESC", (yesterday,)
                )
            else:
                past = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
                self.cursor.execute(
                    "SELECT * FROM alerts WHERE date >= ? ORDER BY id DESC", (past,)
                )
            return self.cursor.fetchall()

    def close(self):
        self.conn.close()
