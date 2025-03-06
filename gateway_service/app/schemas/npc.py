from pydantic import BaseModel
from typing import Optional, Dict, Any


class NPCRequest(BaseModel):
    # model: str = "gpt-4o-mini"
    # model: str = "mistral"
    model: str = "llama3"
    name: str
    personality: str
    backstory: str | None = None
    appearance: str | None = None
    role: str = "neutral"  # For example: warrior, trader, magician


class NPCInput(BaseModel):
    # id: str
    char_descr: str = "You're a knight at the court of Edward I."
    world_descr: str = "You're in London. And it's XIII century."
    has_scratchpad: bool = False
    has_timestamps: bool = False
    is_dreaming: bool = False
    is_planning: bool = False
    # has_long_term_memory: bool = False
    dreaming_prompt: str = None
    planning_prompt: str = None
    # attributes: dict  # Will be stored as JSON


class NPCResponse(BaseModel):
    id: Optional[int] = None  # ID is auto-generated, so it's optional
    name: str
    description: str
    dialogue_sample: str
    attributes: Dict[str, Any]

# id: int
# class SaveNPCRequest(BaseModel):
#     npc: NPCResponse
