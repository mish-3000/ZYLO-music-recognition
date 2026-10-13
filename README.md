# ZYLO — Music Recognition

ZYLO is a Shazam-style music recognition system written in Python. It builds audio fingerprints from your own song library, stores them in PostgreSQL, then records a few seconds of music from your microphone and identifies which song is playing.

```
Press Enter to start recording.
Recording. press Enter to stop
Recording finished
Database is up to date.
song: The Weeknd - The Hills
```

---

## Features

- **Live microphone recognition** — record any length (minimum 3 seconds), press Enter to start and stop.
- **Constellation-map fingerprinting** — spectrogram peaks are paired into compact 32-bit hashes, the same idea used by Shazam.
- **Time-aligned matching** — a song only wins if many hashes line up at the same time offset, so random hash collisions don't produce false matches.
- **Incremental ingestion** — on later runs only newly added songs are fingerprinted.
- **Input checks** — recordings that are too short or too quiet are rejected instead of guessed.

---

## Requirements

| Requirement | Notes |
|---|---|
| **Python** | Tested on Python 3.14 |
| **PostgreSQL** | Any recent version, running on `localhost:5432` |
| **FFmpeg** | On your `PATH`, or `ffmpeg.exe` placed in `downloaders/` |
| **Microphone** | Built-in laptop mic is fine |

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/mish-3000/ZYLO-music-recognition.git
cd ZYLO-music-recognition

python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
```

### 2. Install FFmpeg and PostgreSQL (if you don't have them)

| OS | FFmpeg | PostgreSQL |
|---|---|---|
| Windows | `winget install Gyan.FFmpeg` | [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) |
| macOS | `brew install ffmpeg` | `brew install postgresql && brew services start postgresql` |
| Linux | `sudo apt install ffmpeg` | `sudo apt install postgresql` |

On Linux also run `sudo apt install libportaudio2 libsndfile1` (needed for microphone recording).

### 3. Create the database and tables

Open `psql` (or the Query Tool in pgAdmin) as the `postgres` user and run:

```sql
CREATE DATABASE "SHAZAM";
\c SHAZAM

CREATE TABLE songs (
    id        SERIAL PRIMARY KEY,
    filename  TEXT NOT NULL UNIQUE
);

CREATE TABLE fingerprints (
    hash            BIGINT  NOT NULL,
    song_id         INTEGER NOT NULL,
    time_offset_ms  INTEGER NOT NULL
);

CREATE INDEX idx_hash ON fingerprints (hash);
```

In pgAdmin, run `CREATE DATABASE "SHAZAM";` first, then open a Query Tool on the new `SHAZAM` database and run the rest (skip the `\c` line).

### 4. Set your PostgreSQL password

Open `databaseconn.py` and set your password on this line:

```python
conn = psycopg.connect(host="localhost", dbname="SHAZAM", user="postgres", password="12345678", port="5432", row_factory=dict_row)
```

Do the same in `check.py` if you want to use it.

### 5. Add songs

Create the folder `database/orgFiles/` and put some songs in it. Any format FFmpeg can read works (`.mp3`, `.webm`, `.m4a`, `.wav`, `.flac`, …).

```bash
mkdir database\orgFiles          # Windows
# mkdir -p database/orgFiles     # macOS / Linux
```

The song name shown in results is the file name, so name files like `Artist - Title.mp3`.

---

## Test that it works

1. Put **3–5 songs** in `database/orgFiles/` (a small library keeps the first run fast).
2. Run:
   ```bash
   python matching.py
   ```
3. Press **Enter** to start recording.
4. Play one of those songs **from your phone**, held near the computer's microphone, for **about 10 seconds**.
5. Press **Enter** to stop.

**First run:** after you stop recording, ZYLO converts and fingerprints every song in `database/orgFiles/` before matching. This takes roughly 2–3 seconds per song, and the terminal is quiet while it works.

Expected output:

```
Converted Artist - Song.mp3 to wav format
...
Press Enter to start recording.
Recording. press Enter to stop
Recording finished
Ingesting songs into database...
Ingested 5 songs into database!
song: Artist - Song
```

Later runs skip ingestion (`Database is up to date.`) and answer in a few seconds. To see which songs are stored, run `python check.py`.

---

## Adding more songs later

Drop new files into `database/orgFiles/` and run `python matching.py` again. Only the new songs are converted and fingerprinted:

```
Adding 3 new songs to database...
Added 3 new songs to database.
```

---

## How it works

```
 songs ──► mp3_to_wav ──► spectrogram ──► peak ──► fingerprint ──► PostgreSQL
                                                                     │
 mic ────► test.py ─────► spectrogram ──► peak ──► hashes ──► matching ◄┘
```

1. **Conversion** (`mp3_to_wav.py`) — every song is converted to an 11,025 Hz WAV with FFmpeg. Already-converted songs are skipped.
2. **Spectrogram** (`spectrogram.py`) — the audio is split into 92.8 ms Hann windows with a 46.4 ms hop and converted to decibels.
3. **Peak picking** (`peak.py`) — local maxima are found with a 5×5 maximum filter; the strongest 3 per time frame above 250 Hz and −80 dB are kept.
4. **Fingerprinting** (`fingerprint.py`) — each peak below 1 kHz is paired with up to 11 later peaks (also below 1 kHz) within 50 frames. Each pair becomes a 32-bit hash:
   `frequency A (10 bits) | frequency B (10 bits) | time gap (12 bits)`, stored with the time it occurs in the song.
5. **Storage** (`databaseconn.py`) — hashes go into the `fingerprints` table, indexed by hash.
6. **Recording** (`test.py`) — the microphone clip goes through the exact same steps 1–4.
7. **Matching** (`matching.py`) — every database row sharing a hash with the clip gives a time difference `song time − clip time`. For the correct song these differences are all the same (the point in the song where your clip starts), so they pile up on one value. The song with the biggest pile wins.

### Database schema

Created in [step 3](#3-create-the-database-and-tables).

| Table | Column | Meaning |
|---|---|---|
| `songs` | `id` | Auto-numbered song id |
| | `filename` | Path of the song's WAV file (unique) |
| `fingerprints` | `hash` | 32-bit fingerprint hash (`BIGINT`, since it can exceed the `INTEGER` range) |
| | `song_id` | The song this hash belongs to (`songs.id`) |
| | `time_offset_ms` | Where in the song the hash occurs, in milliseconds |

The `idx_hash` index makes hash lookups fast even with millions of rows.

---

## Project structure

```
├── matching.py        # entry point — records, looks up and prints the matched song
├── test.py            # microphone recording + clip fingerprinting
├── databaseconn.py    # database connection, ingestion of new songs, hash lookup
├── fingerprint.py     # peak pairing and hash generation for songs
├── peak.py            # spectrogram peak picking
├── spectrogram.py     # audio → spectrogram (dB)
├── mp3_to_wav.py      # converts songs in database/orgFiles to WAV
├── check.py           # lists songs stored in the database
├── requirements.txt
└── database/          # created locally, not in git
    ├── orgFiles/      # your songs
    ├── wavFiles/      # converted WAVs (auto)
    └── testClips/     # last recording (auto)
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Error: could not connect to database.` | Make sure PostgreSQL is running, the password in `databaseconn.py` is correct, and the `SHAZAM` database exists (step 3). |
| `relation "songs" does not exist` | The tables haven't been created — run the SQL in step 3 on the `SHAZAM` database. |
| `Error: mp3Files directory not found` | Create `database/orgFiles/` and add songs. |
| `FileNotFoundError` mentioning ffmpeg | Install FFmpeg (see step 2) or put `ffmpeg.exe` in `downloaders/`. |
| `Recording too quiet` | Raise the microphone volume in your OS sound settings and hold the music source closer. |
| `Recording too short` | Record at least 3 seconds; 8–10 seconds gives the most reliable results. |
| Wrong song or `No match found` | Play the song from a **separate device** (phone/speaker). Laptops often apply echo cancellation and noise suppression that remove the computer's own audio and music from the mic. Also check the song is actually in `database/orgFiles/`. |
| First run seems stuck | It is fingerprinting your library — roughly 2–3 seconds per song. Start with a few songs. |

---

## Tech stack

Python · NumPy · SciPy · PostgreSQL (psycopg 3) · sounddevice · soundfile · wavio · FFmpeg
