# Web RAG Chatbot
Web User Interface to Chat with Documents

## Overview
This projet is project is for educational purpose, and its goal is the better understanding of:
- mySQL databases (create table schemas, procedure for more secure practices and authentication)
- ollama and their API
- Rag systems that enable information extraction from documents using llamaindex
- Hugginface

Model used in the repo include:
- "llama3.2" as SLM (Small language model)
- "BAAI/bge-base-en-v1.5" access from huggingface for embeddings
- "openai/whisper-tiny" access from huggingface for audio to text pipeline

If you plan on using this project, you must comply with the licenses and conditions.


## Features
- Summarize Youtube videos using audio transcriptions
- Utilizes models from Ollama and Hugging Face such as phi3 and llama3
- Provides a web user chat interface for interaction
- Parses the YouTube link from the input text, downloads the transcription, and processes it with the LLM.
- Talk with documents in the data folder


## Notes and Observations
- This project was built from knowledge aquired in the repo _carlos-dev-research/vid-audio-summarizer/_ 
- _Noisy Transcriptions:_ When the video transcription contains noisy text, the model is more likely to hallucinate. For example, repetitive nonsensical words that are sometimes output by Whisper Tiny model with complicated text.
- _Progressive Summarization:_ Applying custom loops to summarize information progressively could help compress information and enable the LLM to produce better summaries.
- _NoSQL Databases_: For large scale applications noSQL database could prove more suited for handling chat history, they easier to scale horizontally and the consistency of the chat information is not critical
- _Video Summarization_: the video summarization is not reliable as it depend on pytube and it constantly changing according to how youtube changes it web request structure

## Prerequisites
- A NVIDIA GPU compatible with CUDA.
- Tested on pyton3.10

## Requirements
- **Docker Runtime:** [Install Docker](https://docs.docker.com/engine/install/)
- **NVIDIA CUDA Toolkit:** [Download CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- **NVIDIA Container Toolkit:** [Install NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#configuration)
- **NVIDIA Drivers:** [Download NVIDIA Drivers](https://www.nvidia.com/Download/index.aspx?lang=en-us)

### If using Ubuntu 22 you can use the following
#### Install Docker
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install dockek packages
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker run hello-world
```
#### Install NVIDIA CUDA Toolkit
```bash
# Install NVIDIA container toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-5
```
#### Install NVIDIA Container Toolkit
```bash
# Install nvidia container toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
     tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update

sudo apt-get install -y nvidia-container-toolkit

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```


## Warnings
- **Accuracy:** Content generated by the LLM might be highly inaccurate.
- **Hallucination:** Large videos are more likely to result in hallucinations.
- **Educational Use Only:** The video and image content are not endorsed in any way and are just for educational purposes.

## License
If you plan on using or distributing this project, you must also comply with the licenses of all dependencies and tools used in the project.

## Getting Started
### 1. Clone the Repository
```bash
git clone https://github.com/carlos-dev-research/web-rag-chatbot.git
cd web-rag-chatbot
```

### 2. Build Docker container and get images
```bash
# Get lastest mysql community image
docker pull mysql:latest

# Build docker image form docker file
bash build-docker.sh
```

### 3. Start Services
```bash
# Run the compose Docker to set up containers
docker-compose up
```

### 4. Stop Services
```bash
# Stop the Services if neeeded
docker-compose down
```

### 5. Model should now be running on http://127.0.0.1:5000

## Samples
[Video Preview](https://github.com/carlos-dev-research/web-rag-chatbot/blob/main/video-samples/chat-video.mp4)

