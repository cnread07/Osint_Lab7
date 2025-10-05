import sqlite3
import os
from typing import Iterable, Dict


DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH_DEFAULT = os.path.join(DB_DIR, "osint.db")


def init_db(db_path: str = DB_PATH_DEFAULT):
	os.makedirs(os.path.dirname(db_path), exist_ok=True)
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	cur.execute(
		"""
		CREATE TABLE IF NOT EXISTS osint_data (
			platform TEXT,
			user TEXT,
			timestamp TEXT,
			text TEXT,
			url TEXT UNIQUE,
			sentiment REAL
		)
		"""
	)
	conn.commit()
	conn.close()


def save_to_db(records: Iterable[Dict], db_path: str = DB_PATH_DEFAULT) -> int:
	"""Save records into the DB. Returns number of inserted rows."""
	init_db(db_path)
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	inserted = 0
	for r in records:
		try:
			cur.execute(
				"INSERT OR IGNORE INTO osint_data (platform, user, timestamp, text, url, sentiment) VALUES (?, ?, ?, ?, ?, ?)",
				(
					r.get("platform"),
					r.get("user"),
					r.get("timestamp"),
					r.get("text"),
					r.get("url"),
					r.get("sentiment"),
				),
			)
			if cur.rowcount == 1:
				inserted += 1
		except Exception:
			# skip problematic record
			continue
	conn.commit()
	conn.close()
	return inserted
