curl -X 'POST' \
  'http://0.0.0.0:8001/chat_npc/' \
  -H 'accept: application/json' \
  -H 'Authorization: aYpVtQxRmGzLsBnCfDiKjUxWqHvNwYcFbXlPrVdTw' \
  -H 'Content-Type: application/json' \
  -d '{
  "chat_id": "",
  "npc_id": "5dcc0f0a-2476-4110-8a78-c3137d2314dc",
  "message": "Hello there! How can I find a library?",
  "model": "gpt-4o-mini"
}'

# scratch_pad & timestamp: True: c5bd8c9d-8c30-467f-aff9-2794acefc4d2
# no scratch_pad & timestamp: 5dcc0f0a-2476-4110-8a78-c3137d2314dc