# Base Image
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
SHELL ["/bin/bash", "-c"]


# Copy files
COPY . /App

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    wget \
    python3 \
    python3-pip \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN python3 -m pip install -U pip
RUN python3 -m pip install --no-cache-dir -r /App/requirements.txt

# Install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN mkdir -p /var/log/ollama
RUN nohup ollama start &> /var/log/ollama/ollama.log & sleep 10 && ollama pull llama3.2

# Ensure the entrypoint script is executable
RUN chmod +x /App/entrypoint.sh

WORKDIR /App
RUN python3 first-run.py
EXPOSE 5000

# Set the entrypoint script
ENTRYPOINT ["/App/entrypoint.sh"]