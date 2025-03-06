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
    has_timestamps BOOLEAN NOT NULL,
    is_dreaming BOOLEAN NOT NULL,
    is_planning BOOLEAN NOT NULL,
    dreaming_prompt TEXT NOT NULL,
    planning_prompt TEXT NOT NULL
);

--    name VARCHAR UNIQUE NOT NULL,  -- Unique NPC name
--    description TEXT NOT NULL,
--    dialogue_sample TEXT NOT NULL,
--    attributes JSONB NOT NULL      -- Store attributes as JSONB for efficient queries
--);