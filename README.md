# LLM RAG Project

## Overview

This project builds on top of the main LLM Chat app. It provides RAG functionality on top of the standard chat.
It also features a Gradio chatbot interface for the RAG chat.

This implementation is a baseline vector similarity-based RAG.

## Setup

Follow the installation steps described in the main branch, nothing extra is required.

Retrieval and reranking models are specified in `rag_service/docker-compose.yaml` - don't forget to adjust the ENV at the bottom.
RAG-related parameters along with a prompt template are in `rag_sevice/src/config.py`

## Parametrization

The parameters set during the build:

Retrieval/reranker models, in `rag_service/docker-compose.yaml`:
- `command:` pass a model as `--model-id`
- `environment:` `EMB_MODEL`

If you need to switch to a gpu set TEI containers accordingly:
- `image:` https://github.com/huggingface/text-embeddings-inference?tab=readme-ov-file#docker-images

Retrieval parameters are in `rag_service/src/config.py`

Rag-gradio model is in `rag_gradio_service/src/config.py`, `OPENAI_MODEL`

The default parameters of a RAG request are in `rag_service/src/main.py`, `RAGRequest`

## Usage

RAG endpoints use the same authorization scheme as the main chat service. 
To utilize RAG start by adding documents to your vector DB using the dedicated endpoint:

```python
import requests
import os

docs_path = "/path/to/your/docs/dir"

for doc in os.listdir(docs_path):
    doc_path = os.path.join(docs_path, doc)
    if os.path.isfile(doc_path):
        text = open(doc_path).read()
        resp = requests.post(
            "http://0.0.0.0:8001/add_to_rag_db/",
            json={"text": text},
            headers={"Authorization": os.getenv("YOUR_TOKEN")}
        )
        if resp.status_code != 200: 
            print(f"error uploading document {doc}")
```
Documents are expected to be preprocessed (chunked [1](https://towardsdatascience.com/rag-101-chunking-strategies-fdc6f6c2aaec), [2](https://antematter.io/blogs/optimizing-rag-advanced-chunking-techniques-study) etc).

If you have a lot of documents (>100k) you may benefit from indexing your document table (more on this [here]()).
You can do it as follows:
```commandline
curl -H "Authorization: <YOUR TOKEN>" -X GET http://0.0.0.0:8001/reindex/
```

On inference, you can send a request with the following parameters:
```commandline
    query: str - the text query 
    chat_id: Optional[str] - chat id to maintain conversation history
    model: str = "gpt-4o-mini" - name of an LLM
    use_reranker: bool = True - whether to rerank after retreival
    top_k_retrieve: int = 20 - num of items to retrieve
    top_k_rank: int = 4 - num of items to return after reranking
    max_out_tokens: int = 512 - max num of tokens. Used to drop retrieved pieces 
        of content if total prompt length goes beyond max contex length.
```
Note you can optionally use a reranker ([3](https://www.pinecone.io/learn/series/rag/rerankers/)).
Both embedding and reranking models are light enough to run on a cpu.

To access the Gradio interface, open `http://0.0.0.0:7860` in a browser.

## Note

Every query submitted via the gradio interface goes through the context retrieval stage,
which means multi-turn dialogue may not work as expected. E.g. for a query "and you?", what may make
sense given the conversation history, irrelevant context will likely be retrieved, which will negatively affect generation quality.

Note that calls to RAG endpoints count toward the rate limit, as they use the chat endpoint under the hood.

