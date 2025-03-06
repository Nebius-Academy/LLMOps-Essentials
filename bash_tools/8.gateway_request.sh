curl -X POST "http://localhost:8001/generate_npc/" \
-H "Authorization: $(echo $ADMIN_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "model": "llama3",
  "name": "Billy",
  "personality": "Gloomy man",
  "appearance": "Old man not very clean"
}'
