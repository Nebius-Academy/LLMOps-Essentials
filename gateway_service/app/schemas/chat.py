from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    model: str
    chat_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    chat_id: str


class ChatNPCRequest(BaseModel):
    chat_id: str | None = None
    npc_id: str
    message: str
    model: str
    # scratchpad_prompt: str = "You can use scratchpad for thinking before you answer: whatever you output between #SCRATCHPAD and #ANSWER won't be shown to anyone. You start your output with #SCRATCHPAD and after you've done thinking, you #ANSWER"
