import psycopg
from psycopg.rows import dict_row

conn = psycopg.connect(host="localhost", dbname="SHAZAM", user="postgres", password="12345678", port="5432", row_factory=dict_row)
cursor = conn.cursor()
cursor.execute("SELECT id, filename FROM songs ORDER BY id;")
for row in cursor.fetchall():
    print(row)
cursor.close()
conn.close()