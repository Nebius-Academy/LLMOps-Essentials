import httpx, json, os
import logging
from app.db.database import database
from app.db.models import npcs
from app.core.security import verify_token
from app.schemas.npc import NPCRequest, NPCResponse
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.sql import insert, select, or_
from sqlalchemy import update

# from app.core.config import INFERENCE_ROUTING

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# model_name = os.getenv("MODEL_NAME")

# if not model_name:
#     raise HTTPException(status_code=500, detail="MODEL_NAME environment variable is not set")

# logger.info(f"Model name: {model_name}")


@router.post("/generate_npc/", dependencies=[Depends(verify_token)])
async def generate_npc(npc_request: NPCRequest) -> NPCResponse:
    """
    Generates NPC on the input data
    """
    prompt = f"""
    You are an AI that outputs only JSON. No explanations, comments, or extra text.

    Create an NPC with these characteristics:
    - Name: {npc_request.name}
    - Personality: {npc_request.personality}
    - Role: {npc_request.role}
    - Look: {npc_request.appearance or 'None'}
    - History: {npc_request.backstory or 'None'}

    Respond **only** in valid JSON format:
    {{
      "description": "NPC description here.",
      "dialogue_sample": "NPC dialogue example here.",
      "attributes": {{
        "Power": 0-10,
        "Intellect": 0-10,
        "Charisma": 0-10
      }}
    }}
    """


    url = "http://ollama:11434/api/generate"  # Ollama endpoint
    model_name = npc_request.model  # Example: "mistral", "gemma", "llama3"

    # url = f"http://{INFERENCE_ROUTING[npc_request.model]}:8000/chat/"
    logger.info(f"Url: {url}")
    logger.info(f"Prompt: {prompt}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json={"model": model_name, "prompt": prompt, "stream": False, "format": "json"},
                timeout=httpx.Timeout(120.0),
            )
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting: {exc}")
            raise HTTPException(status_code=500, detail="LLM API is not reachable")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="LLM is not available")

    # try:
    #     response_ad = json.loads(response['response'])
    #     # logger.info(f"Response_ad: {response_ad}")
    # except json.JSONDecodeError:
    #     logger.error("Failed to parse DIRECT LLM response as JSON.")
    #     raise HTTPException(status_code=500, detail="Invalid response format from LLM")

    response_text = await response.aread()
    logger.error(f"Raw response: {response_text}")
    decoded_text = response_text.decode("utf-8")  # Convert bytes to string
    response_json = json.loads(decoded_text)  # Parse string to JSON

    try:
        result = json.loads(response_json['response'])
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response as JSON.")
        raise HTTPException(status_code=500, detail="Invalid response format from LLM")

    logger.info(f"Result: {result}")

    return NPCResponse(
        name=npc_request.name,
        description=result.get("description", "No description available"),
        dialogue_sample=result.get("dialogue_sample", "No dialogue sample available"),
        attributes=result.get("attributes", {})
    )
    # attributes=str(result.get("attributes", {}))  # Convert attributes to string for safe handling


@router.post("/save_npc/", dependencies=[Depends(verify_token)])
async def save_npc(save_request: NPCResponse):
    """
    Saving of the generated NPC to the database
    """
    query = (
        insert(npcs)
        .values(
            # id=npc_id,  # Assigning the UUID
            name=save_request.name,
            description=save_request.description,
            dialogue_sample=save_request.dialogue_sample,
            attributes=save_request.attributes,
        )
        .returning(npcs.c.id)  # Return the newly generated ID
    )

    try:
        npc_id = await database.execute(query)
        return {"status": "NPC successfully saved", "npc_id": npc_id}
    except Exception as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Error saving NPC")


@router.get("/search_npc/", dependencies=[Depends(verify_token)])
async def search_npc(
        name: str = Query(None, description="Search by NPC name"),
        min_charisma: int = Query(None, description="Minimum charisma: 1-10"),
        min_intellect: int = Query(None, description="Minimum intellect: 1-10"),
        min_strength: int = Query(None, description="Minimum strength:1-10")
):
    """
    Search for NPCs based on name or attributes.
    """
    query = select(npcs)

    if name:
        query = query.where(npcs.c.name == name)

    if min_charisma or min_intellect or min_strength:
        query = query.where(
            or_(
                (npcs.c.attributes["Charisma"].as_integer() >= min_charisma) if min_charisma else None,
                (npcs.c.attributes["Intellect"].as_integer() >= min_intellect) if min_intellect else None,
                (npcs.c.attributes["Strength"].as_integer() >= min_strength) if min_strength else None
            )
        )

    try:
        results = await database.fetch_all(query)
        return {"results": results}
    except Exception as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Error searching NPCs")


@router.put("/edit_npc/", dependencies=[Depends(verify_token)])
async def edit_npc(
        name: str,  # The NPC's name (must be unique)
        description: str = Query(None, description="New description for the NPC"),
        dialogue_sample: str = Query(None, description="New dialogue sample for the NPC"),
        attributes: dict = Body(None, description="New attributes for the NPC (JSON format)")
):
    """
    Edit an NPC's details based on the provided data.
    Name is the primary identifier and cannot be changed.
    """
    query = update(npcs).where(npcs.c.name == name)

    # Set the fields that are provided
    set_fields = {}

    if description is not None:
        set_fields["description"] = description
    if dialogue_sample is not None:
        set_fields["dialogue_sample"] = dialogue_sample
    if attributes is not None:
        set_fields["attributes"] = attributes

    # Apply the updates
    if set_fields:
        query = query.values(set_fields)

        try:
            result = await database.execute(query)
            if result == 0:
                raise HTTPException(status_code=404, detail=f"NPC with name '{name}' not found")
            return {"status": "NPC successfully updated"}
        except Exception as e:
            logging.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Error updating NPC")
    else:
        raise HTTPException(status_code=400, detail="No fields to update provided")
