import json
import logging

import httpx
import tiktoken
from config import EMBED_URL, LANCE_TABLE, PROMPT_TOKEN_LIMIT, RAG_PROMPT
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from semantic_search import rerank, retrieve

app = FastAPI()
# https://github.com/openai/tiktoken/blob/c0ba74c238d18b4824c25f3c27fc8698055b9a76/tiktoken/model.py#L20
oai_tokenizer = tiktoken.get_encoding("o200k_base")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGRequest(BaseModel):
    query: str
    chat_id: str | None = None
    model: str = "gpt-4o-mini"
    use_reranker: bool = False
    top_k_retrieve: int = 20
    top_k_rank: int = 4
    max_out_tokens: int = 512


class AddToDBRequest(BaseModel):
    text: str


class RAGResponse(BaseModel):
    message: str
    context: list[str]


def prepare_message(
    query: str, docs: list[str], max_out_tokens: int
) -> (str, list[str]):
    """
    An attempt to truncate the context not to go over token limit
    """
    context = "\n".join(docs)
    message = RAG_PROMPT.format(context=context, query=query)

    while (
        docs
        and len(oai_tokenizer.encode(message)) > PROMPT_TOKEN_LIMIT - max_out_tokens
    ):
        docs.pop()
        context = "\n".join(docs)
        message = RAG_PROMPT.format(context=context, query=query)
        logger.warning(
            f"Context was reduced due to the token limit. "
            f"Prompt was {len(oai_tokenizer.encode(message))} tokens long"
        )

    message = oai_tokenizer.decode(
        oai_tokenizer.encode(message)[: (PROMPT_TOKEN_LIMIT - max_out_tokens)]
    )

    return message, docs


@app.post("/prompt_w_context/")
async def prompt_w_context(rag_request: RAGRequest) -> RAGResponse:
    """
    Retrieves relevant documents and constructs a prompt

    :param rag_request: query and other relevant params
    :return: final prompt and a list of retrieved documents
    """
    if rag_request.use_reranker:
        retrieved_docs = await retrieve(rag_request.query, rag_request.top_k_retrieve)
        documents = await rerank(
            rag_request.query, retrieved_docs, rag_request.top_k_rank
        )
    else:
        documents = await retrieve(rag_request.query, rag_request.top_k_rank)

    message, documents = prepare_message(
        query=rag_request.query,
        docs=documents,
        max_out_tokens=rag_request.max_out_tokens,
    )

    return RAGResponse(message=message, context=documents)


@app.post("/add_to_rag_db/")
async def add_to_db(add_to_db_request: AddToDBRequest):
    """
    Adds a single text document to a vector DB.

    :param add_to_db_request: text to add to a DB
    :raises HTTPException: if embedding service is unavailable
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                EMBED_URL,
                json={"inputs": add_to_db_request.text},
                timeout=httpx.Timeout(60.0),
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=500, detail="Failed to connect to TEI service"
            )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="TEI service error"
        )
    vector = json.loads(response.content)[0]

    data = [{"vector": vector, "text": add_to_db_request.text}]
    LANCE_TABLE.add(data=data)


@app.get("/reindex/")
async def reindex():
    """
    Creates a new index for docs table

    :raises HTTPException: on indexing error
        An example is when # items in the table < default # clusters (256)
    """
    try:
        LANCE_TABLE.create_index()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
