set -e

export MODEL_NAME=gpt-4o-mini
cd inference_service
poetry install
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --reload
