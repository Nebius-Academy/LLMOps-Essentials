set -e

export MODEL_NAME=meta-llama/Meta-Llama-3.1-8B-Instruct
export CACHE_DIR=/usr/models
cd inference_service
poetry install
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
