from app.db.database import metadata
from sqlalchemy import Column, String, Integer, Table, Boolean
from sqlalchemy.dialects.postgresql import JSONB

users = Table(
    "users",
    metadata,
    Column("username", String, primary_key=True),
    Column("hashed_password", String),
    Column("api_key", String, unique=True),
)

# npcs = Table(
#     "npcs",
#     metadata,
#     Column("id", Integer, primary_key=True, autoincrement=True),  # Auto-incrementing ID
#     Column("name", String, nullable=False, unique=True),  # Keep name unique but not as a primary key
#     Column("description", String, nullable=False),
#     Column("dialogue_sample", String, nullable=False),
#     Column("attributes", JSONB, nullable=False),
# )

npcs = Table(
    "npcs",
    metadata,
    Column("id", String, primary_key=True),
    Column("char_descr", String, nullable=False),
    Column("world_descr", String, nullable=False),
    Column("has_scratchpad", Boolean, nullable=False),
    Column("has_timestamps", Boolean, nullable=False),
    Column("is_dreaming", Boolean, nullable=False),
    Column("is_planning", Boolean, nullable=False),
    # Column("has_long_term_memory", Boolean, nullable=False),
    Column("dreaming_prompt", String, nullable=False),
    Column("planning_prompt", String, nullable=False),
)