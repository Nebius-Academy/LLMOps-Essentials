import os

DATABASE_URL = "postgresql://user:password@postgres/dbname"
ADMIN_TOKEN = os.getenv("ADMIN_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
RATE_LIMIT = 5  # max requests per minute
RATE_LIMIT_KEY_PREFIX = "rate_limit"
INFERENCE_ROUTING = {"gpt-4o-mini": "gpt-4-mini", "gpt-4o": "gpt-4o",
                     "meta-llama/Meta-Llama-3.1-405B-Instruct": "llama-405B",
                     "meta-llama/Meta-Llama-3.1-70B-Instruct": "llama-70B", 
                     "meta-llama/Meta-Llama-3.1-8B-Instruct": "llama-8B"}
CHAT_MEMORY_LENGTH = 3
