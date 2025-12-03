import sqlite3
from pathlib import Path

DB_PATH = Path("marketwatcher.db")


def get_conn():
    """Return a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the listings table if it does not exist."""
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT,
            listing_id TEXT,
            title TEXT,
            price REAL,
            currency TEXT,
            url TEXT,
            brand TEXT,
            size TEXT,
            condition TEXT,
            image_url TEXT,
            created_at TEXT,
            scraped_at TEXT
        );
        """
    )

    conn.commit()
    conn.close()
