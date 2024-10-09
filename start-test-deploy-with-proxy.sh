#!/bin/bash

# Prompt for the public IP address
echo "Enter Public IP Address of the server:"
read public_ip

# Change to the reverse-proxy directory, check if it exists first
if [ -d "reverse-proxy" ]; then
    cd reverse-proxy
else
    echo "Error: 'reverse-proxy' directory does not exist."
    exit 1
fi

# Run the Python script to build the config files
python3 build-config-files.py "$public_ip"

# Check if the Python script ran successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to run the Python script."
    exit 1
fi


# Run the Docker Compose command
cd ..
docker compose -f docker-compose-proxy.yml up -d

# Check if Docker Compose ran successfully
if [ $? -eq 0 ]; then
    echo "Docker Compose started successfully."
else
    echo "Error: Docker Compose failed to start."
    exit 1
fi
