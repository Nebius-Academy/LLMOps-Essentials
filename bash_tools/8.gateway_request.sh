curl -X 'POST' \
  'http://0.0.0.0:8001/chat_npc/' \
  -H 'accept: application/json' \
  -H 'Authorization: aYpVtQxRmGzLsBnCfDiKjUxWqHvNwYcFbXlPrVdTw' \
  -H 'Content-Type: application/json' \
  -d '{
  "chat_id": "",
  "npc_id": "5dcc0f0a-2476-4110-8a78-c3137d2314dc",
  "message": "Hello there! How can I find a library?",
  "model": "meta-llama/Meta-Llama-3.1-405B-Instruct"
}'
