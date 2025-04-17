from pydantic import BaseModel


class NPCInput(BaseModel):
    # id: str
    char_descr: str = "You're a knight at the court of Edward I."
    world_descr: str = "You're in London. And it's XIII century."
    has_scratchpad: bool = False