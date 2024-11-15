from pydantic import BaseModel


class RAGRequest(BaseModel):
    query: str
    chat_id: str | None = None
    model: str = "gpt-4o-mini"
    use_reranker: bool = False
    top_k_retrieve: int = 20
    top_k_rank: int = 4
    max_out_tokens: int = 512


class RAGResponse(BaseModel):
    response: str
    chat_id: str | None = None


class AddToDBRequest(BaseModel):
    text: str
