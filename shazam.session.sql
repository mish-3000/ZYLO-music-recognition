CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL UNIQUE
);

CREATE TABLE fingerprints (
    hash BIGINT NOT NULL,
    song_id INT NOT NULL,
    time_offset_ms INT NOT NULL
);

CREATE INDEX idx_hash ON fingerprints(hash);
