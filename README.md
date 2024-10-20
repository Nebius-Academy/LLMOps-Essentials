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
## License

This project is licensed under the GNU GPL v3 License. See the [LICENSE](LICENSE) file for more information.

© Nebius BV, 2024
