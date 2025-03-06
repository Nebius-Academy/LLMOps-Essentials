import httpx, json, os
import logging
import uuid
from app.db.database import database
from app.db.models import npcs
from app.core.security import verify_token
from app.schemas.npc import NPCInput, NPCResponse
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.sql import insert, select, or_
from sqlalchemy import update

# from app.core.config import INFERENCE_ROUTING

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/create_npc/", dependencies=[Depends(verify_token)])
async def create_npc(npc_input: NPCInput):
    """
    Generates NPC on the input data
    """
    npc_id = str(uuid.uuid4())

    query = (
        insert(npcs)
        .values(
            id=npc_id,  # Insert the UUID as the primary key
            char_descr=npc_input.char_descr,
            world_descr=npc_input.world_descr,
            has_scratchpad=npc_input.has_scratchpad,
            has_timestamps=npc_input.has_timestamps,
            is_dreaming=npc_input.is_dreaming,
            is_planning=npc_input.is_planning,
            dreaming_prompt=npc_input.dreaming_prompt,
            planning_prompt=npc_input.planning_prompt
        )
    )

    # has_long_term_memory=npc_input.has_long_term_memory,
    try:
        await database.execute(query)
        return {"status": "NPC successfully saved", "npc_id": npc_id}
    except Exception as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Error creating NPC")
