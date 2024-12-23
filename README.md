# Topic 3. Run open source LLM

## Overview

This branch shows how to deploy open source LLM locally inside the inference service using FastAPI.


## Environment Variables

To run the inference server with open source LLM you need to specify the next variables: 

- **`MODEL_NAME`**: The name of the model to be used by the inference service.
- **`CACHE_DIR`**: A directory to load or store the weights of a local model. It's optional and can be left unspecified. In this case, the default path will be used.

Note: You no longer need the **`OPENAI_API_KEY`** environment variable. Now, you make requests to the local model.

Example:

```bash
export MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct"
export CACHE_DIR="/path/to/your/local/storage/llama3-8b"
```

## Usage

**Run the Inference Service** :
   ```bash
   cd inference_service
   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```
After running an inference server, you can easily check that everything is working well with the following bash script:
   ```bash
   ./bash_tools/2.inference_request.sh
   ```

## Deployment

### Basic Deployment with Docker Compose

To deploy the services using Docker Compose:

1. **Specify environment variables:**
	```bash
   source ./bash_tools/0.init_env.sh 
   export MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct"
   export CACHE_DIR="/path/to/your/local/storage/llama3-8b"
   export HF_TOKEN=INSERT_YOUR_HUGGINGFACE_TOKEN_HERE
   ```
   **Note**: t is important to specify `CACHE_DIR` and ensure that the folder exists. This will allow the reuse of already downloaded model weights.
2. **Build the Docker Images:**
   ```bash
   docker-compose build
   ```

3. **Start the Services:**
   ```bash
   docker-compose up
   ```
4. **Verify that the GPU is detected inside the Docker container.** Check the logs for a line similar to the following:
	```text
	INFO:src.main:CUDA is avaliable: True
	```
5. **Wait for the weights to load.** This may take some time. Once completed, you will see a line in the logs:
	```text
	INFO:src.main:Inference server is ready for requests...
	```
6. **Send the first request to the gateway.** For reference, you can use the provided Bash script:
	```bash
	source ./bash_tools/5.gateway_request.sh 
	```

Docker Compose will use the `Dockerfile` located in each service directory (`gateway_service` and `inference_service`) to build the images and start the containers.

## License

This project is licensed under the GNU GPL v3 License. See the [LICENSE](LICENSE) file for more information.

© Nebius BV, 2024
