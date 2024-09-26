#!/bin/bash

# Start the ollama service in the background
nohup ollama start &> /var/log/ollama/ollama.log &

# Wait a bit to ensure the service starts properly
sleep 10

python3 run.py