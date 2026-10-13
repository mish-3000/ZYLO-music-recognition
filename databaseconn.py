import psycopg
import os
from psycopg.rows import dict_row
from test import allHashes

try:
    conn = psycopg.connect(host="localhost", dbname="SHAZAM", user="postgres", password="12345678", port="5432", row_factory=dict_row)
except psycopg.OperationalError as e:
    print("Error: could not connect to database.")
    print(f"Details: {e}")
    exit()

cursor = conn.cursor()


cursor.execute("SELECT COUNT(*) FROM songs")
db_song_count = cursor.fetchone()['count']


from mp3_to_wav import wavFilesPaths
from fingerprint import hashes

cursor.execute("SELECT filename FROM songs")
existing_names = set(os.path.basename(row['filename']) for row in cursor.fetchall())
newFiles = [f for f in wavFilesPaths if os.path.basename(f) not in existing_names]

if db_song_count == 0:
    print("Ingesting songs into database...")
    hashesCache = hashes(wavFilesPaths)
    for filename,combinations in hashesCache.items():
        cursor.execute("INSERT INTO songs (filename) VALUES (%s) ON CONFLICT(filename) DO NOTHING RETURNING id", (filename,))
        result = cursor.fetchone()
        if result is not None:
            song_id=result['id']
        else:
            cursor.execute("SELECT id FROM songs WHERE filename=%s", (filename,))
            result = cursor.fetchone()
            song_id=result['id']
        bulkData = []
        for hash, time in combinations:
            bulkData.append(( hash, song_id, time*0.0464*1000))
        cursor.executemany("INSERT INTO fingerprints (hash, song_id, time_offset_ms) VALUES (%s, %s, %s)", bulkData)
    cursor.execute("CREATE TEMPORARY TABLE unique_fingerprints AS SELECT DISTINCT hash, song_id, time_offset_ms FROM fingerprints;")
    cursor.execute("DELETE FROM fingerprints;")
    cursor.execute("INSERT INTO fingerprints (hash, song_id, time_offset_ms) SELECT hash, song_id, time_offset_ms FROM unique_fingerprints;")
    cursor.execute("DROP TABLE unique_fingerprints;")
    print(f"Ingested {db_song_count + len(hashesCache)} songs into database!")

elif newFiles:
    print(f"Adding {len(newFiles)} new songs to database...")
    hashesCache = hashes(newFiles)
    for filename,combinations in hashesCache.items():
        cursor.execute("INSERT INTO songs (filename) VALUES (%s) ON CONFLICT(filename) DO NOTHING RETURNING id", (filename,))
        result = cursor.fetchone()
        if result is not None:
            song_id=result['id']
        else:
            cursor.execute("SELECT id FROM songs WHERE filename=%s", (filename,))
            result = cursor.fetchone()
            song_id=result['id']
        bulkData = []
        for hash, time in combinations:
            bulkData.append(( hash, song_id, time*0.0464*1000))
        cursor.executemany("INSERT INTO fingerprints (hash, song_id, time_offset_ms) VALUES (%s, %s, %s)", bulkData)
    print(f"Added {len(newFiles)} new songs to database.")

else:
    print("Database is up to date.")

hash_list = list(allHashes.keys())
cursor.execute("SELECT * FROM fingerprints WHERE hash = ANY(%s)", (hash_list,))
results = cursor.fetchall()
  
conn.commit()