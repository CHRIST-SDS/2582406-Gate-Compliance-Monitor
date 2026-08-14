"""
Syncs the CSV export from the existing library system (data/library_profiles.csv)
into a local SQLite DB, and provides lookup helpers used by the compliance engine.
"""
import os
import sqlite3
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "library.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "library_profiles.csv")


class LibraryDB:
    def __init__(self, db_path: str = DB_PATH, csv_path: str = CSV_PATH):
        self.db_path = db_path
        self.csv_path = csv_path
        self._sync_from_csv()

    def _sync_from_csv(self):
        """Loads/refreshes the SQLite table from the library system's CSV export."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(
                f"{self.csv_path} not found. Run `python -m src.dummy_data_generator` first, "
                f"or replace with a real library-system export."
            )
        df = pd.read_csv(self.csv_path)
        conn = sqlite3.connect(self.db_path)
        df.to_sql("profiles", conn, if_exists="replace", index=False)
        conn.close()

    def lookup(self, reg_no: str) -> dict | None:
        if reg_no is None:
            return None
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT reg_no, name, department, card_expiry, library_status "
                    "FROM profiles WHERE reg_no = ?", (reg_no,))
        row = cur.fetchone()
        conn.close()
        if row is None:
            return None
        reg_no, name, dept, expiry, status = row
        is_expired = datetime.strptime(expiry, "%Y-%m-%d") < datetime.now()
        return {
            "reg_no": reg_no,
            "name": name,
            "department": dept,
            "card_expiry": expiry,
            "library_status": status,
            "is_expired": is_expired,
        }
