CREATE TABLE IF NOT EXISTS users (
    username VARCHAR PRIMARY KEY,
    hashed_password VARCHAR,
    api_key VARCHAR UNIQUE
);
