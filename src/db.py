import os
import sqlite3


class OffloaderDB:

    def __init__(self, db_path):
        # Expand ~/ to full user path
        db_path = os.path.expanduser(db_path)
        # Ensure the parent directory exists
        db_dir = os.path.dirname(db_path)
        if not os.path.isdir(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        # Now open (or create) the SQLite file
        self.conn = sqlite3.connect(db_path)
        self.ensure_tables()

    def ensure_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS configs (
            key TEXT PRIMARY KEY,
            value TEXT
        )"""
        )
        self.conn.commit()

    def get_configs(self):
        cur = self.conn.cursor()
        cur.execute("SELECT key, value FROM configs")
        rows = cur.fetchall()
        configs = {key: eval(value) for key, value in rows}

        defaults = self.get_default_configs()
        return {**defaults, **configs}

    def save_configs(self, configs):
        cur = self.conn.cursor()
        for key, value in configs.items():
            cur.execute(
                """
            INSERT OR REPLACE INTO configs (key, value)
            VALUES (?, ?)
            """,
                (key, repr(value)),
            )
        self.conn.commit()

    @staticmethod
    def get_default_configs():
        return {
            "extensions": ["mp3", "wav", "mp4"],
            "excluded_dirs": [],
            "min_file_size_mb": 1,
            "file_age_days": 30,
        }
