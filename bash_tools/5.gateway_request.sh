curl -X POST "http://localhost:8001/chat/" \
-H "Authorization: $(echo $ADMIN_KEY)" \

-d '{
  "message": "What is poetry in Python?",
  "model": "gpt-4o-mini"
}'