import sqlite3
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent.parent
DB = BASE / 'db.sqlite3'

if not DB.exists():
    print('Database not found at', DB)
    sys.exit(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

print('--- tables ---')
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for row in cur.fetchall():
    print(row[0])

print('\n--- jobs_job columns (PRAGMA table_info) ---')
try:
    cur.execute("PRAGMA table_info('jobs_job')")
    cols = cur.fetchall()
    for c in cols:
        print(c)
    names = [c[1] for c in cols]
    print('\nHas latitude?', 'latitude' in names)
except Exception as e:
    print('Error fetching jobs_job info:', e)

print('\n--- jobs migrations in django_migrations ---')
try:
    cur.execute("SELECT id, app, name, applied FROM django_migrations WHERE app='jobs' ORDER BY id")
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print('Error fetching migrations:', e)

conn.close()
