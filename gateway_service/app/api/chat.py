import base64, os
import json
import uuid
import re, datetime
from app.core.config import ADMIN_TOKEN, INFERENCE_ROUTING, CHAT_MEMORY_LENGTH, MODEL_NAME
import logging

import httpx
from app.core.metrics import update_tokens_in, update_tokens_out
from app.core.security import verify_token, verify_admin_token
from app.db.database import redis, database
from app.db.models import npcs
from sqlalchemy import select
from app.schemas.chat import ChatRequest, ChatResponse, ChatNPCRequest
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_chat_id() -> str:
    """
    Generates a short, URL-safe, unique chat ID.

    This function generates a UUID, converts it to a string, encodes it using URL-safe base64 encoding,
    and takes the first 22 characters of the resulting string to create a compact, unique identifier.

    :returns: The chat ID
    :rtype: str
    """
    random_uuid = uuid.uuid4()
    uuid_str = str(random_uuid).replace("-", "")
    base64_encoded = base64.urlsafe_b64encode(uuid_str.encode())
    short_id = base64_encoded.decode("utf-8").rstrip("=")

    return short_id[:22]


@router.post("/chat/", dependencies=[Depends(verify_token)])
async def chat_proxy(chat_request: ChatRequest) -> ChatResponse:
    """
    Handles chat proxying requests by interacting with a chat service and storing chat history in Redis.

    :param chat_request: The request payload containing the chat ID and message.
    :type chat_request: ChatRequest
    :return: The response from the chat service encapsulated in a ChatResponse object.
    :rtype: ChatResponse
    """
    chat_id = chat_request.chat_id
    if chat_request.chat_id is not None:
        chat_history = await redis.lrange(f"chat_history:{chat_request.chat_id}", 0, -1)
        chat_history = [json.loads(msg.decode()) for msg in chat_history]
    else:
        chat_id = generate_chat_id()
        chat_history = []

    url = f"http://{INFERENCE_ROUTING[chat_request.model]}:8000/chat/"
    logger.info(f"Url: {url}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://{INFERENCE_ROUTING[chat_request.model]}:8000/chat/",
                json={"message": chat_request.message, "chat_history": chat_history},
                timeout=httpx.Timeout(60.0),
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=500, detail="Failed to connect to chat service"
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Chat service error"
        )

    await redis.rpush(
        f"chat_history:{chat_id}",
        json.dumps({"text": chat_request.message, "role": "user"}),
    )
    await redis.rpush(
        f"chat_history:{chat_id}",
        json.dumps({"text": response.json()["response"], "role": "assistant"}),
    )
    response_text = response.json()["response"]

    update_tokens_in(len(chat_request.message.split()))
    update_tokens_out(len(response_text.split()))

    return ChatResponse(response=response_text, chat_id=chat_id)


@router.get("/chat/{user_id}/{chat_id}/history", dependencies=[Depends(verify_admin_token)])
async def get_chat_history(chat_id: str, user_id: str):
    """
    Retrieves the chat history for the given chat_id from Redis.

    :param chat_id: The ID of the chat to retrieve history for
    :type chat_id: str
    :param user_id: User ID associated with the chat
    :type user_id: str
    :return: A dictionary containing the chat_id and its history
    :rtype: dict
    :raises HTTPException: If chat history is not found
    """
    redis_key = f"chat_history:{user_id}:{chat_id}"
    chat_history = await redis.lrange(redis_key, 0, -1)

    if not chat_history:
        raise HTTPException(status_code=404, detail="Chat history not found for this user")

    decoded_history = [msg.decode() for msg in chat_history]
    return {"chat_id": chat_id, "user_id": user_id, "history": decoded_history}


async def get_npc(npc_id: str):
    query = select(npcs).where(npcs.c.id == npc_id)
    npc = await database.fetch_one(query)
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    return npc


# @router.post("/chat_npc/", dependencies=[Depends(verify_token)])
@router.post("/chat_npc/")
async def chat_npc_proxy(chat_request: ChatNPCRequest, api_key: str=Depends(verify_token)) -> ChatResponse:
    """
    Handles chat proxying requests with NPC by interacting with a chat service and storing chat history in Redis.

    :param chat_request: The request payload containing the chat ID and message.
    :type chat_request: ChatRequest
    :return: The response from the chat service encapsulated in a ChatResponse object.
    :rtype: ChatResponse

    Parameters
    ----------
    api_key - Password of the user
    """
    is_admin = api_key == ADMIN_TOKEN  # Check if the API key is the admin key
    chat_id = chat_request.chat_id
    user_id = api_key
    long_mem_key = f"long_memory:{user_id}:{chat_id}"  # Store long-term memory
    logger.info(f"user_id: {user_id}")
    if chat_id is not None:
        chat_key = f"chat_history:{user_id}:{chat_id}"
        messages = await redis.lrange(chat_key, 0, -1)
        chat_history = [json.loads(msg.decode()) for msg in messages]
    else:
        chat_id = generate_chat_id()
        chat_history = []
    logger.info(f"chat_id: {chat_id }")
    # Limit the number of messages provided to LLM
    short_history = chat_history[-CHAT_MEMORY_LENGTH:] if len(chat_history) > CHAT_MEMORY_LENGTH else chat_history

    # Load long-term memory (summary)
    long_memory = await redis.get(long_mem_key)
    long_memory = long_memory.decode() if long_memory else ""  # Convert from bytes to string if exists

    npc = await get_npc(chat_request.npc_id)

    if npc.has_scratchpad:
        npc.char_descr += """You can use scratchpad for thinking before you answer: whatever you output between #SCRATCHPAD and #ANSWER won't be shown to anyone.
You start your output with #SCRATCHPAD and after you've done thinking, you #ANSWER. """

    npc.char_descr += """The actual user's message will start with #USER:"""

    if long_memory != "":
        long_memory = "### PREVIOUS DIALOGUE:" + long_memory

    sys_mes = f"""WORLD SETTING: {npc.world_descr}
###
{npc.char_descr}
{long_memory}
            """
    user_message_to_save = f"\n\n#USER: {chat_request.message}"
    chat_request.message = user_message_to_save

    logger.info(f"system message: {sys_mes}")
    logger.info(f"user message: {chat_request.message}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"http://{INFERENCE_ROUTING[chat_request.model]}:8000/chat_npc/",
                json={"sys_mes": sys_mes, "message": chat_request.message, "chat_history": short_history}, #chat_history
                timeout=httpx.Timeout(60.0),
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=500, detail="Failed to connect to chat service"
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Chat service error"
        )

    response_text = response.json()["response"]
    response_clean = response_text
    if npc.has_scratchpad:
        scratchpad_match = re.search(r"#SCRATCHPAD(:?)(.*?)#ANSWER(:?)", response_text, re.DOTALL)
        if scratchpad_match:
            response_clean = response_text[scratchpad_match.end():].strip()

    # await redis.rpush(
    #     f"chat_history:{chat_id}",
    #     json.dumps({"text": chat_request.message, "role": "user"}),
    # )
    # await redis.rpush(
    #     f"chat_history:{chat_id}",
    #     json.dumps({"text": response.json()["response"], "role": "assistant"}),
    # )

    await redis.rpush(
        f"chat_history:{user_id}:{chat_id}",  # Now includes user_id
        json.dumps({"text": chat_request.message, "role": "user"}),
    )

    await redis.rpush(
        f"chat_history:{user_id}:{chat_id}",  # Store response in the same key
        json.dumps({"text": response.json()["response"], "role": "assistant"}),
    )

    # # Trim the list to keep only the last N messages
    # await redis.ltrim(f"chat_history:{user_id}:{chat_id}", -chat_request.max_length, -1)

    logger.info(f"chat history saved: {user_id}:{chat_id}")

    update_tokens_in(len(chat_request.message.split()))
    update_tokens_out(len(response_text.split()))

    logger.info(f"response: {response_text}")
    logger.info(f"user response: {response_clean}")

    return ChatResponse(response=response_clean, chat_id=chat_id)


@router.post("/end_chat_session/")
async def end_chat_session(chat_id: str, api_key: str = Depends(verify_token)):
    """
    Ends a chat session and summarizes chat history.

    :param chat_id: The chat session ID to summarize
    :type chat_id: str
    """
    user_id = api_key
    chat_key = f"chat_history:{user_id}:{chat_id}"
    long_mem_key = f"long_memory:{user_id}:{chat_id}"
    logger.info(f"Ending chat session for user_id: {user_id}, chat_id: {chat_id}")

    # Load chat history
    messages = await redis.lrange(chat_key, 0, -1)
    chat_history = [json.loads(msg.decode()) for msg in messages] if messages else []

    if not chat_history:
        raise HTTPException(status_code=400, detail="Chat history is empty, no need to summarize.")

    short_history = chat_history[-CHAT_MEMORY_LENGTH:] if len(chat_history) > CHAT_MEMORY_LENGTH else chat_history
    logger.info(f"Short history: {short_history}")

    history_prompt_part = ""
    if short_history:
        for message in short_history:
            if message["role"] == "user":
                history_prompt_part += f"""{message["text"]}"""
            else:
                history_prompt_part += f"""{message["text"]}"""

    long_mem_key = f"long_memory:{user_id}:{chat_id}"  # Store long-term memory
    # Load long-term memory (summary)
    long_memory = await redis.get(long_mem_key)
    long_memory = long_memory.decode() if long_memory else ""  # Convert from bytes to string if exists
    logger.info(f"Long memory: {long_memory}")

    if long_memory != "":
        summary_prompt = f"""Reflect on the previous conversation and your previous memories about yourself.

        CURRENT SELF MEMORIES: {long_memory}.

        PREVIOUS CONVERSATION: {history_prompt_part}

        ---
        What have you learnt about yourself, the user, your goals, and the world around? Answer in no more than 10 sentences. 
        Your answer won't be shown to anyone.
        """
        # summary_prompt = f""" Summarize the following conversation between a user and an NPC while keeping key details.
        # Take into account previous dialogue: {long_memory}.
        # Current message history: {history_prompt_part}.
        # Start answering with no additional description of your summary.
    # """
    else:
        # Generate a summary using LLM
        # summary_prompt = f"""
        # Summarize the following conversation between a user and an NPC while keeping key details:
        # {history_prompt_part}.
        # Start answering with no additional description of your summary.
        # """
        summary_prompt = f"""Reflect on the previous conversation and your previous memories about yourself.

        PREVIOUS CONVERSATION: {history_prompt_part}

        ---
        What have you learnt about yourself, the user, your goals, and the world around? Answer in no more than 10 sentences. 
        Your answer won't be shown to anyone.
        """

    model_name = os.getenv("MODEL_NAME")
    logger.info(f"summary_prompt: {summary_prompt}")
    logger.info(f"Model name: {model_name}")

    async with httpx.AsyncClient() as client:
        summary_response = await client.post(
            f"http://{INFERENCE_ROUTING[model_name]}:8000/chat_npc/",  #'gpt-4o-mini'
            json={"sys_mes": summary_prompt, "message": "", "chat_history": []},
            timeout=httpx.Timeout(60.0),
        )

    if summary_response.status_code == 200:
        summary_text = summary_response.json()["response"]

        # Append the new summary to existing long_memory
        updated_long_memory = summary_text
        await redis.set(long_mem_key, updated_long_memory)  # Store updated long-term memory

        logger.info(f"Updated long memory: {updated_long_memory}")

        # Clear short-term history since it's now summarized
        # await redis.delete(chat_key)

        return {"status": "Chat session ended, summary saved", "summary": summary_text}

    else:
        raise HTTPException(status_code=500, detail="Failed to generate summary")
