import psycopg2
import psycopg2.extras
from fingerprint import hashes
from test import allHashes
conn=psycopg2.connect(host="localhost", database="SHAZAM", user="postgres", password="12345678", port="5432")
cursor=conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

for filename,combinations in hashes().items():
    cursor.execute("INSERT INTO songs (filename) VALUES (%s) RETURNING id", (filename,))
    song_id = cursor.fetchone()[0]
    bulkData = []
    for hash, time in combinations:
        bulkData.append(( hash, song_id, time*0.0464*1000))  # Convert time to milliseconds
    cursor.executemany("INSERT INTO fingerprints (hash, song_id, time_offset_ms) VALUES (%s, %s, %s)", bulkData)
cursor.execute("CREATE TEMPORARY TABLE unique_fingerprints AS SELECT DISTINCT hash, song_id, time_offset_ms FROM fingerprints;")
cursor.execute("DELETE FROM fingerprints;")
cursor.execute("INSERT INTO fingerprints (hash, song_id, time_offset_ms) SELECT hash, song_id, time_offset_ms FROM unique_fingerprints;")
cursor.execute("DROP TABLE unique_fingerprints;")

hash_list = list(allHashes.keys())
cursor.execute("SELECT * FROM fingerprints WHERE hash = ANY(%s)", (hash_list,))
results = cursor.fetchall()
cursor.execute("SELECT * FROM fingerprints")
all_rows = cursor.fetchall()     
        
conn.commit()
cursor.close()
conn.close()