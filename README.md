# LLM Chat Project

## Overview

This project implements a gateway service integrated with an inference service using FastAPI. The gateway service acts as the entry point for all user interactions, handling authentication, rate limiting, logging, and API routing, while the inference service processes requests and interacts with external APIs (such as OpenAI). This project leverages Poetry for dependency management and supports deployment via Docker Compose and Kubernetes.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Installation](#installation)
3. [Environment Variables](#environment-variables)
4. [Usage](#usage)
   - [User's Entrypoint](#users-entrypoint)
5. [Deployment](#deployment)
   - [Basic Deployment with Docker Compose](#basic-deployment-with-docker-compose)
   - [Advanced Deployment with Kubernetes](#advanced-deployment-with-kubernetes)
6. [Poetry: Dependency Management](#poetry-dependency-management)
   - [Installing Poetry](#installing-poetry)
7. [License](#license)

## Project Structure

```
.
├── LICENSE
├── README.md
├── SECURITY.md
├── docker-compose.yaml
├── gateway_service
│   ├── Dockerfile
│   ├── app
│   │   ├── __init__.py
│   │   ├── api
│   │   ├── core
│   │   ├── db
│   │   ├── main.py
│   │   ├── middleware
│   │   └── schemas
│   ├── poetry.lock
│   └── pyproject.toml
├── inference_service
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── src
│       └── main.py
├── k8s
│   ├── gateway-service-deployment.yaml
│   ├── gpt-4-mini-deployment.yaml
│   ├── gpt-4o-deployment.yaml
│   ├── postgres-deployment.yaml
│   └── redis-deployment.yaml
├── postgres_init
│   └── init.sql
└── rag_service
    └── data
        ├── models--BAAI--bge-small-en-v1.5
        ├── models--mixedbread-ai--mxbai-rerank-base-v1
        └── tmp
```

## Installation for Development

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Poetry and Dependencies

Ensure Poetry is installed on your system. You can install it using the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Next, install the project dependencies:

```bash
poetry install
```

## Environment Variables

This project requires several environment variables to be set up correctly. Below are the necessary environment variables and their purpose:

- **`OPENAI_API_KEY`**: The API key for accessing the OpenAI service, required by the inference service.
- **`MODEL_NAME`**: The name of the model to be used by the inference service.
- **`ADMIN_KEY`**: A secret token used for administrative access to certain endpoints in the gateway service.
- **`DATABASE_URL`**: The URL of the database that the gateway service connects to.
- **`RATE_LIMIT`**: Configures the rate limit for API requests, as defined in the `config.py` file of the gateway service.

You can set these variables in your shell before running the services:

```bash
export OPENAI_API_KEY=your_openai_api_key
export MODEL_NAME="gpt-4"
export ADMIN_KEY="your_admin_key"
export DATABASE_URL="postgresql://user:password@postgres/dbname"
```

For development, you might also want to use a `.env` file to load these variables automatically.

For the code to be able to work with PostgreSQL, you need to do a little database management and
attach to the DB's container and run this query in `psql`:

```postgresql
CREATE TABLE users (
    username VARCHAR PRIMARY KEY,
    hashed_password VARCHAR,
    api_key VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS npcs (
    id VARCHAR UNIQUE PRIMARY KEY,
    char_descr TEXT NOT NULL,
    world_descr TEXT NOT NULL,
    has_scratchpad BOOLEAN NOT NULL
);

```

## Usage

### User's Entrypoint

The user's entry point to the system is the **Gateway Service**. This service handles all incoming requests from clients, performing tasks such as:

- **Authentication**: Verifying user credentials and tokens.
- **Rate Limiting**: Controlling the number of requests a user can make within a certain time period.
- **Logging**: Recording requests and responses for monitoring and debugging.
- **Routing**: Directing requests to the appropriate internal services, such as the Inference Service.

#### Starting the Gateway Service

1. **Run the Gateway Service**:
   ```bash
   cd gateway_service
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

   The gateway service will listen for requests on the specified port (default is `http://localhost:8001`).

2. **Run the Inference Service** (if needed):
   ```bash
   cd inference_service
   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Main commands to work with NPC factory

### Create NPC
    
You can create NPC with the following data structure:
```json
{
  "char_descr": "You're a knight at the court of Edward I.",
  "world_descr": "You're in London. And it's XIII century.",
  "has_scratchpad": false
}
```
where: 
char_descr - description of the character,
world_descr - description of the world,
has_scratchpad - if the character is having a 
scratchpad or not (to think on the users question before answering) 

To run a request with the data you can use the following command:
```bash
curl -X 'POST' \
  'http://0.0.0.0:8001/create_npc/' \
  -H 'accept: application/json' \
  -H 'Authorization: aYpVtQxRmGzLsBnCfDiKjUxWqHvNwYcFbXlPrVdTw' \
  -H 'Content-Type: application/json' \
  -d '{
  "char_descr": "You'\''re a knight at the court of Edward I.",
  "world_descr": "You'\''re in London. And it'\''s XIII century.",
  "has_scratchpad": true
}'
```

The result of the request will be JSON with chat_id which will be used for 
all the following chat requests with this character within this session:
```json
{
  "status": "NPC successfully saved",
  "npc_id": "0d2c9254-8bd8-42a0-8fe0-ae76e408abe7"
}
```
### To chat with NPC

Request params:
```json
{
  "chat_id": "ZjlhOWY2ZTdjY2Y0NDVmMW",
  "npc_id": "5dcc0f0a-2476-4110-8a78-c3137d2314dc",
  "message": "Oh wow! Your math knowledge is much better than mine. I was not able to solve this one. Can you multiply? What is 3 times 8?",
  "model": "meta-llama/Meta-Llama-3.1-405B-Instruct"
}
```
Request:
```bash
curl -X 'POST' \
  'http://0.0.0.0:8001/chat_npc/' \
  -H 'accept: application/json' \
  -H 'Authorization: token8438316761499410150' \
  -H 'Content-Type: application/json' \
  -d '{
  "chat_id": "ZjlhOWY2ZTdjY2Y0NDVmMW",
  "npc_id": "5dcc0f0a-2476-4110-8a78-c3137d2314dc",
  "message": "Oh wow! Your math knowledge is much better than mine. I was not able to solve this one. Can you multiply? What is 3 times 8?",
  "model": "meta-llama/Meta-Llama-3.1-405B-Instruct"
}'
```

### To end session

```bash
curl -X 'POST' \
  'http://0.0.0.0:8001/end_chat_session/?chat_id=ZjlhOWY2ZTdjY2Y0NDVmMW' \
  -H 'accept: application/json' \
  -H 'Authorization: token8438316761499410150' \
  -d ''
```

### To get chat history
For admins only
```bash
curl -X 'GET' \
  'http://0.0.0.0:8001/chat/token8438316761499410150/ZjlhOWY2ZTdjY2Y0NDVmMW/history' \
  -H 'accept: application/json' \
  -H 'Authorization: aYpVtQxRmGzLsBnCfDiKjUxWqHvNwYcFbXlPrVdTw'
```
where the admin key should be provided for 'Authorization'


## Deployment

### Basic Deployment with Docker Compose

To deploy the services using Docker Compose:

1. **Build the Docker Images:**
   ```bash
   docker-compose build
   ```

2. **Start the Services:**
   ```bash
   docker-compose up
   ```

Docker Compose will use the `Dockerfile` located in each service directory (`gateway_service` and `inference_service`) to build the images and start the containers.

### Advanced Deployment with Kubernetes

For advanced deployment using Kubernetes:

1. **Set up the Kubernetes cluster:**

   Ensure you have a running Kubernetes cluster. You can use Minikube for local development or any managed Kubernetes service for production.

2. **Deploy the Services:**

   Deploy the individual components using the provided YAML files located in the `k8s` directory.

   ```bash
   kubectl apply -f k8s/postgres-deployment.yaml
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/gateway-service-deployment.yaml
   kubectl apply -f k8s/gpt-4-mini-deployment.yaml
   ```

3. **Verify the Deployment:**

   Use the following command to check the status of the deployed pods:

   ```bash
   kubectl get pods
   ```

   Ensure all services are running correctly. If any service is not running, check the logs with:

   ```bash
   kubectl logs <pod-name>
   ```

### Notes on Kubernetes

- **Persistence**: Ensure persistent storage is configured for databases if required.
- **Ingress**: Set up an Ingress controller to manage external access to the services.
- **Scaling**: You can scale the services by adjusting the `replicas` field in the respective deployment YAML files.

## Poetry: Dependency Management

### What is Poetry?

Poetry is a tool for managing dependencies and packaging in Python. It allows you to declare the libraries your project depends on and ensures you have the right versions installed. Poetry also helps to build and publish your packages, making it a robust solution for Python project management.

### Installing Poetry

To install Poetry, run the following command in your terminal:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

This script installs Poetry globally on your system. Once installed, you can use Poetry to manage your project's dependencies, create virtual environments, and handle other project-related tasks.

### Key Commands

- **Installing Dependencies**: Install all dependencies declared in the `pyproject.toml` file.
  ```bash
  poetry install
  ```

- **Adding a Dependency**: Add a new dependency to your project.
  ```bash
  poetry add <package-name>
  ```

- **Running Your Project**: Run your project within the Poetry environment.
  ```bash
  poetry run python <script.py>
  ```

- **Publishing a Package**: Build and publish your package to PyPI.
  ```bash
  poetry publish
  ```

## License

This project is licensed under the GNU GPL v3 License. See the [LICENSE](LICENSE) file for more information.

© Nebius BV, 2024
