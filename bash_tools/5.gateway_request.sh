curl -X POST "http://localhost:8001/chat/" \
-H "Authorization: $(echo $ADMIN_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "message": "What is poetry in Python?",
  "model": "llama3-8b"
}'
