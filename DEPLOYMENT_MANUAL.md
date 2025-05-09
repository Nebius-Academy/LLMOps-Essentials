# Intro

This manual will help you to deploy any branch of this repo using Docker. We strongly recommend using Docker; otherwise you may run into all sorts of trouble - the MLOps road is tough!

We'll describe how to do it in Nebius cloud. In other environments the algorithm should be mostly the same.

## If you choose Nebius cloud for the deployment

### Getting started

Register in [Nebius](https://auth.eu.nebius.com/ui/login). This will give you access to the [console](https://console.eu.nebius.com/).

In the console, choose **Compute** in the left menu and press **Create Resource -> Virtual Machine**.

We suggest choosing either of these VMs:

*	No GPU, the default one, if you want to use LLMs available via API.
*	L40s, if you want to use a self-served LLM.

Don’t forget to stop the virtual machine after you finish experimenting! It costs you money when it runs. Moreover, even with a stopped virtual machine, you pay for disk space. So if you’re sure that you don’t need the VM, delete it together with the disk volume
While creating a VM, you’ll need to do the following things:

*	Choose a VM name; we’ll refer to it as `vm_name` (save it somewhere!)
*	Choose a VM administrator name; we’ll refer to it as `user_name` (save it somewhere!)
*	Back on your machine, generate an SSH key (using the command `ssh-keygen -t ed25519` in a terminal). Two files will be generated: `llmops-ssh-key` and `llmops-ssh-key.pub`. Actually, it’s a good idea to give the file exactly this name to avoid confusion further in this manual.
  You’ll need to paste the content of `llmops-ssh-key.pub` in the SSH key box during VM creation. Make sure there are no trailing spaces or newlines at the end of the string.	
* In the public address checkbox, choose **“Auto assign static ip”**. 

Now, press **Create VM** at the bottom of the page. This will create a VM. It will be up and running in a minute or so. To find it, click the **Compute** left menu item again.

<center>
<img src="https://drive.google.com/uc?export=view&id=1IBinQ8lotiKUZpgCfRL5rs1Hh47OBPTH" width=600 />
</center>

After it starts, click on it to see its properties. Copy the **expernal public IP address** and save it somewhere. We’ll refer to it as `public_ip` in bash code or `public_ip` in Python code. Public IP is crucial for allowing your VM to communicate with the outside world. (Though it's not the safest way.)

<center>
<img src="https://drive.google.com/uc?export=view&id=1NRcJUSL-_tk8xWZ5ecnBYFC-7R1uwRmB" width=600 />
</center>

To connect to the VM, do the following.

Open a terminal. Make sure that the `llmops-ssh-key` file is in your current directory (run ls to check it, if needed). Run

```bash
ssh user_name@public_ip -i llmops-ssh-key
```

**with the right `user_name` and `public_ip`** - you need those you created and saved earlier! Enter “yes” if prompted by the system. This will connect you to the VM and allow to execute commands there.

If you get disconnected from the login (for example, due to inactivity timeout), just run the same command again.

## Setting up the docker

The following recipe will work in Nebius Cloud and should generally work on Ubuntu machines; however `sudo` permissions may or may not be needed depending on your system's settings. If you use some other cloud or deploy locally, modify this instruction to fit your system.

1. Clone the repo to the VM. Run
   
  *	`git clone https://github.com/Nebius-Academy/LLMOps-Essentials/` (main branch) if you just want to set up a chat service, 
  *	`git clone -b rag_service --single-branch https://github.com/Nebius-Academy/LLMOps-Essentials/` if you want to use RAG,
  *	`git clone -b open-source-llm --single-branch https://github.com/Nebius-Academy/LLMOps-Essentials/` if you want to have a chat service with a self-served LLM, 
  *	Change to another branch, if needed.

  Now, you should have LLMOps-Essentials folder in your current directory. Run `ls` to check if it’s so.

2. Change directory to get inside the LLMOps-Essentials folder:

  ```bash
  cd LLMOps-Essentials
  ```

3. Some of the things we’ll be doing during setup require root access rights (using `sudo` when needed). If you're using Nebius Cloud, consider switching to the superuser:

  ```bash
  sudo su
  ```

4. Now, if you don't have docker-compose installed, run the following bash code: 

  ```bash
  sudo apt-get update
  apt install docker-compose
  ```
  This will install docker-compose, which in unfortunately of the earlier version than we may need. So, next we download the latest version of docker-compose:
  
  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  ```
  
  and make it executable:
  
  ```bash
  sudo chmod +x /usr/local/bin/docker-compose
  ```

  You can now check the docker’s version and make sure it’s more recent than 2.20:
  
  ```bash
  docker-compose version
  ```

5. Now, you’ll need to set up several environmental variables required by the docker container we’ll be using. The following two should be run in any case:

  ```bash
  source bash_tools/0.init_env.sh
  export DATABASE_URL="postgresql://user:password@postgres/dbname"
  ```

  Make sure you set them for the root user. The first script sets the **ADMIN_KEY** required for the chat service’s admin user to do anything with it.

  To be absolutely sure, you may check that ADMIN_KEY is saved:

  ```bash
  echo $ADMIN_KEY
  ```

  It should output a non-empty string.

  There are several more case-specific things to set up.
  
  a. For a chat service with APIs or a RAG service:

  ```bash
  export OPENAI_API_KEY=<YOUR OPENAI API KEY>
  export NEBIUS_API_KEY=<YOUR NEBIUS API KEY>
  ```
  
  By default you'll need both, because the app launches services for both OpenAI and Nebius models. See the **Adding/removing models** section for details about changing the models list.
  
  b. For a self-served LLM-based chat service:
  
  ```bash
  export MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct"
  export CACHE_DIR="/path/to/your/local/storage/llama3-8b"
  export HF_TOKEN=<INSERT_YOUR_HUGGINGFACE_TOKEN_HERE>
  ```

  Note that you need a Hugging Face token.
  
  Feel free to change the model name and the cache directory name appropriately if you want to use another model. Just make sure that your GPU is large enough.

6. The two final commands build the docker container and actually get the service running:

  ```
   docker-compose build
   docker-compose up
   ```

  Your current terminal tab now shows the service in waiting regime. 

  From this tab, you can also terminate the service whenever you wish (**ctrl+C** or **cmd+C** on Mac).

  If you understand that you did something wrong, you can run the following commands to clear everything you’ve done in docker:
  
  ```bash
  docker kill $(docker ps -q)
  docker system prune -f 
  docker volume prune -f 
  docker network prune -f
  ```

  This will stop all the running containers and clean everything.

7. Rejoice!

# Using the service

In this section, we’ll discuss how to call the services from both bash and Jupyter notebook. All the service calls will be either GET or POST requests; for example:

```bash
curl -X POST "http://<your_public_ip>:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=username,&password=password"
```

(Just don't forget to enter the correct public IP!)

Note that if you send the request from the same virtual machine where the docker is up, you can use `localhost` as the `public_ip`.

Because you’ll be using the public IP many times, you may consider saving it as an environmental variable using 

```bash
export PUBLIC_IP=<YOUR PUBLIC IP>
```

In this case, you can further use it like this:

```bash
curl -X POST "http://${PUBLIC_IP}:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=username,&password=password"
```

Since your VM has an external IP address, you can send requests to it from any other machine. From colab as well! And no need to connect to it via ssh. Let's see how.

## Access and permissions

To send requests to the service you’ll need an API key. You can use **ADMIN_KEY** from `bash_tools/0.init_env.sh`, which we set up as an environmental variable for the root user during the preparations, but that’s not cool. So, let’s learn how to register a new user.

First of all choose a username and a password: `<your_username>` and `<your_password>`. Then run the following command:

### With bash:

```bash
curl -X POST "http://PUBLIC_IP:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=<your_username>,&password=<your_password>"
```

For example:

```bash
curl -X POST "http://235.184.143.30:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=John_Smith,&password=Pasw0rd"
```

This command returns something like

```bash
{"message":"User created successfully.","api_key":"token4724306863716988259"}
```

Now, to access the service the user will need this the `api_key` string. In this example it’s `token4724306863716988259`. Save it to the **SERVICE_KEY** environmental variable or to the `service_key` Python variable.

### With Python:

```python
import requests

public_ip = <YOUR_PUBLIC_IP>

username = <YOUR_USERNAME>
password = <YOUR_PASSWORD>

url = f"http://{public_ip}:8001/signup/"
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "username": username,
    "password": password
}

response = requests.post(url, headers=headers, data=data)

import json

response_dict = json.loads(response.text)
api_token = response_dict['api_key']
api_token
```

## Querying the chat service (if it’s API, i.e. if it's not the open-source-llm branch) 

At the moment the chat service supports APIs of OpenAI and Nebius AI Studio. Namely, you can use the following models:

* **gpt-4o-mini**
*	**gpt-4o**
*	**meta-llama/Meta-Llama-3.1-405B-Instruct**
*	**meta-llama/Meta-Llama-3.1-70B-Instruct**
*	**meta-llama/Meta-Llama-3.1-8B-Instruct**

Each of them runs as a separate service in the docker. See the **Adding/removing models** part of the guide if you want to change this list.

Now, how to query a model:

### With bash

```bash
curl -X POST "http://PUBLIC_IP:8001/chat/" \
-H "Authorization: $(echo $SERVICE_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "message": "What is poetry in Python?",
  "model": "gpt-4o-mini"
}'
```

### With Python

```python
response = requests.post(
            f"http://{public_ip}:8001/chat/",
            json={
  "message": "Tell me about Baldurs Gate?",
  "model": "meta-llama/Meta-Llama-3.1-70B-Instruct"
            },
            headers={"Authorization": service_key}
        )
response
```

## Querying the chat service (if the LLM is self-served; open-source-llm branch of the repo) 

At the moment, the service only serves one open-source LLM: the one defined by the **MODEL_NAME** environmental variable. However, we didn’t change the interface, and the user still needs to specify the model in the POST request. The rule of the names is the same, and it involves the **INFERENCE_ROUTING** variable, which is a dictionary **“How the model is called by the user”:”The name of the service”**. By default, it has

```
“llama3-8b”:”llama3-8b”
```

Now, how to query this model:

### With bash

```bash
curl -X POST "http://PUBLIC_IP:8001/chat/" \
-H "Authorization: $(echo $SERVICE_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "message": "What is poetry in Python?",
  "model": "llama3-8b"
}'
```

### With Python

```python
response = requests.post(
            f"http://{public_ip}:8001/chat/",
            json={
  "message": "Tell me about Baldurs Gate!",
  "model": "llama3-8b"
            },
            headers={"Authorization": service_key}
        )
```

## Adding a string to the RAG database [only for the RAG service]

### With bash:

```bash
curl -X POST "http://PUBLIC_IP:8001/add_to_rag_db/" \
-H "Authorization: $(echo $SERVICE_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "text": "All you need is LLMOps"
}'
```

If successful, returns None.

### With Python:

```python
entry = "All you need is LLMOps"

response = requests.post(
            f"http://{public_ip}:8001/add_to_rag_db/",
            json={"text": entry},
            headers={"Authorization": service_key}
)
if response.status_code != 200:
        # Means that it failed
```

## Querying the RAG service (chat + retrieval)

### With bash:

```bash
curl -X POST "http://PUBLIC_IP:8001/rag/" \
-H "Authorization: $(echo $SERVICE_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "query": "Hi there! What do you know about LLMOps?",
  "model": "gpt-4o-mini",
  "use_reranker": true,
  "top_k_retrieve": 5,
  "top_k_rank": 2,
  "max_out_tokens": 1024
}'
```

### With Python:

```python
response = requests.post(
            f"http://{public_ip}:8001/rag/",
            json={
    "query": "Tell me about Baldur’s Gate!",
    "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "use_reranker": True,
    "top_k_retrieve": 5,
    "top_k_rank": 2,
    "max_out_tokens": 1024
            },
            headers={"Authorization": service_key}
        )
```

# Adding/removing models (for the API-based branches)

Every model is provided by a separate service. The services are described in the `docker-compose.yaml` file. Here is an example of such a service:

```bash
  llama-70b:
    build: ./inference_service
    container_name: inference_service_llama_3_1_70b
    ports:
      - "8005:8000"
    environment:
      NEBIUS_API_KEY: ${NEBIUS_API_KEY}
      CLIENT_NAME: "nebius"
      MODEL_NAME: "meta-llama/Meta-Llama-3.1-70B-Instruct"
```

The user queries a model by its huggingface name, and the app should somehow understand how to map `"meta-llama/Meta-Llama-3.1-70B-Instruct"` to the service called `"llama-70B"`. For that, we have the `INFERENCE_ROUTING` dictionary defined in `gateway_service/app/core/config.py`. By default it looks like this:

```python
INFERENCE_ROUTING = {"gpt-4o-mini": "gpt-4-mini", "gpt-4o": "gpt-4o",
                     "meta-llama/Meta-Llama-3.1-405B-Instruct": "llama-405B",
                     "meta-llama/Meta-Llama-3.1-70B-Instruct": "llama-70B", 
                     "meta-llama/Meta-Llama-3.1-8B-Instruct": "llama-8B"}
```

So, to remove a model you need to:

1. Remove the corresponding service from `docker-compose.yaml`
2. Remove the corresponding entry from `INFERENCE_ROUTING`

**Note**. Even you remove all the services providing OpenAI models, you won't remove the need to set up **OPENAI_API_KEY**. To get rid of it for good, you'll need to ditch its mentions from `inference_service/src/main.py` and `docker-compose.yaml` - and also from `k8s/gpt-4o-deployment.yaml` and `k8s/gpt-4-mini-deployment.yaml` if you use k8s.

The same for adding! You need to:

1. Add a service to `docker-compose.yaml`. Just copypaste one of the existing services, give it a unique name and port, and set up the model name.
2. Add the corresponding entry to `INFERENCE_ROUTING`

## What if you want to use some other API provider?

Nebius AI Studio API and OpenAI API both use `OpenAI` client, and this makes them easily interchangeable. To use some other API, you'll have to change the client call, which is defined in `inference_service/src/main.py`.
