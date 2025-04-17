set -e

#export MODEL_NAME='gpt-4o-mini'
docker compose build
docker compose up
#--build -d
