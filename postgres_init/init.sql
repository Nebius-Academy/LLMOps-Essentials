CREATE TABLE IF NOT EXISTS users (
    username VARCHAR PRIMARY KEY,
    hashed_password VARCHAR,
    api_key VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS npcs (
    id VARCHAR UNIQUE PRIMARY KEY,
    char_descr TEXT NOT NULL,
    world_descr TEXT NOT NULL,
    has_scratchpad BOOLEAN NOT NULL,
);

