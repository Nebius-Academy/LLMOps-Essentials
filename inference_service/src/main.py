import logging
import os
import functools

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from transformers import pipeline, AutoTokenizer
import torch


MODEL_NAME = os.environ.get("MODEL_NAME")
# Load the model from CACHE_DIR if specified. Otherwise, use the default path
CACHE_DIR = os.environ.get("CACHE_DIR", default=None)


# Load the model using FastAPI lifespan event to load the LLM only once
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model from HuggingFace transformers library
    global llm_pipeline

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        use_fast=False
    )
    llm_pipeline = pipeline(
        "text-generation",
        model=MODEL_NAME,
        tokenizer=tokenizer,
        model_kwargs={
            "torch_dtype": torch.bfloat16,
            "cache_dir": CACHE_DIR,
        },
        device_map="auto",
        # It's important to specify max number of tokens that the model can
        # work with. The maximum value is model_max_length. The model can work
        # faster if you set the value lower.
        max_length=tokenizer.model_max_length,
        # Ask a model to return only generated text, without inputs
        return_full_text=False,
    )

    # It's possible to predefine parameters like sampling, temperature,
    # max_new_tokens, etc. here.
    llm_pipeline = functools.partial(
        llm_pipeline,
        eos_token_id=llm_pipeline.tokenizer.eos_token_id,
    )

    yield

    # Clean up GPU memory
    del tokenizer, llm_pipeline
    torch.cuda.empty_cache()


# Initialize the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Message(BaseModel):
    text: str
    role: str


class ChatRequest(BaseModel):
    message: str
    chat_history: list[Message]


class ChatResponse(BaseModel):
    response: str


@app.post("/chat/")
async def chat_with_llm(chat_request: ChatRequest) -> ChatResponse:
    try:
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            *[
                {"role": msg.role, "content": msg.text}
                for msg in chat_request.chat_history
            ],
            {"role": "user", "content": chat_request.message},
        ]
        response = llm_pipeline(messages)
        return ChatResponse(response=response[0]["generated_text"])
    except ValueError as ve:
        # Log the error with traceback
        logger.error(f"ValueError error: {str(ve)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ValueError error: {str(ve)}")
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
