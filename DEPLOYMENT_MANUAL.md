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

The following recipe will work in Nebius Cloud. If you use some other cloud or deploy locally, modify this instruction to fit your system.

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

There are several more case-specific things.
a.	For a chat service with APIs or a RAG service:
export OPENAI_API_KEY=<YOUR OPENAI API KEY>
export NEBIUS_API_KEY=<YOUR NEBIUS API KEY>
b.	For a self-served LLM-based chat service:
export MODEL_NAME="meta-llama/Meta-Llama-3.1-8B-Instruct"
export CACHE_DIR="/path/to/your/local/storage/llama3-8b"
export HF_TOKEN=<INSERT_YOUR_HUGGINGFACE_TOKEN_HERE>
Feel free to change the model name and the cache directory name appropriately if you want to use another model. Just make sure that your GPU is large enough.


7.	The two final commands build the docker container and actually get the service running:
docker-compose build
docker-compose up

Your current terminal tab now shows the service in waiting regime. 

From this tab, you can also terminate the service whenever you wish (ctrl+C or cmd+C on Mac).

If you understand that you did something wrong, you can run the following commands to clear everything you’ve done in docker:
docker kill $(docker ps -q)
docker system prune -f 
docker volume prune -f 
docker network prune -f
This will stop all the running containers and clean everything.

8.	Rejoice!

Using the service
In this section, we’ll discuss how to call the services from both bash and Jupyter notebook. All the service calls will be either GET or POST requests; for example:
curl -X POST "http://PUBLIC_IP:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=username,&password=password"

Note that if you send the request from the same virtual machine where the docker is up, you can use localhost as the public_ip.
Because you’ll be using the public IP many times, you may consider saving it as an environmental variable using 
export PUBLIC_IP=<YOUR PUBLIC IP>
In this case, you can further use it like this:
curl -X POST "http://${PUBLIC_IP}:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=username,&password=password"
Access and permissions
To send requests to the service you’ll need an API key. You can use ADMIN_KEY from bash_tools/0.init_env.sh, which we set up as an environmental variable for the root user during the preparations, but that’s not cool. So, let’s learn how to register a new user
With bash:
curl -X POST "http://PUBLIC_IP:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=username,&password=password"

For example:
curl -X POST "http://235.184.143.30:8001/signup/" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=John_Smith,&password=Pasw0rd"

This command returns something like
{"message":"User created successfully.","api_key":"token4724306863716988259"}
Now, to access the service the user will need this the api_key string. In this example it’s token4724306863716988259. Save it to the SERVICE_KEY environmental variable or to the service_key Python variable.
With Python:

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

Querying the chat service (if it’s API; main branch of the repo) 
At the moment the chat service supports APIs of OpenAI and Nebius AI Studio. Namely, you can use the following models:
•	gpt-4o-mini
•	gpt-4o
•	meta-llama/Meta-Llama-3.1-405B-Instruct
•	meta-llama/Meta-Llama-3.1-70B-Instruct 
•	meta-llama/Meta-Llama-3.1-8B-Instruct
Each of them runs as a separate service in the docker.
If you want to add another model by OpenAI or another model served by Nebius AI Studio, you’ll need to:
a.	Add a corresponding service to docker-compose.yaml
b.	Add this model to the INFERENCE_ROUNTING variable in gateway_service/app/core/config.py. Note that INFERENCE_ROUNTING is a dictionary “How the model is called by the user”:”The name of the service”
Now, how to query a model:
With bash
curl -X POST "http://PUBLIC_IP:8001/chat/" \
-H "Authorization: $(echo $SERVICE_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "message": "What is poetry in Python?",
  "model": "gpt-4o-mini"
}'

With Python
response = requests.post(
            f"http://{public_ip}:8001/chat/",
            json={
  "message": "Tell me about Baldurs Gate?",
  "model": "meta-llama/Meta-Llama-3.1-70B-Instruct"
            },
            headers={"Authorization": service_key}
        )
response

Querying the chat service (if the LLM is self-served; open-source-llm branch of the repo) 
At the moment, the service only serves one open-source LLM: the one defined by the MODEL_NAME environmental variable. However, we didn’t change the interface, and the user still needs to specify the model in the POST request. The rule of the names is the same, and it involves the INFERENCE_ROUTING variable, which is a dictionary “How the model is called by the user”:”The name of the service”. By default, it has
“llama3-8b”:”llama3-8b”
With bash
curl -X POST "http://PUBLIC_IP:8001/chat/" \
-H "Authorization: $(echo $SERVICE_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "message": "What is poetry in Python?",
  "model": "llama3-8b"
}'

With Python
response = requests.post(
            f"http://{public_ip}:8001/chat/",
            json={
  "message": "Tell me about Baldurs Gate!",
  "model": "llama3-8b"
            },
            headers={"Authorization": service_key}
        )

Adding a string to the RAG database [only for the RAG service]
With bash:
curl -X POST "http://PUBLIC_IP:8001/add_to_rag_db/" \
-H "Authorization: $(echo $SERVICE_KEY)" \
-H "Content-Type: application/json" \
-d '{
  "text": "All you need is LLMOps"
}'

If successful, returns None.

With Python:
entry = "All you need is LLMOps"

response = requests.post(
            f"http://{public_ip}:8001/add_to_rag_db/",
            json={"text": entry},
            headers={"Authorization": service_key}
)
if response.status_code != 200:
        # Means that it failed

Querying the RAG service (chat + retrieval)

With bash:

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

With Python:


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




