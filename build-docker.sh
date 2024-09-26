#!/bin/bash
IMAGE_NAME="web-rag-chatbot:01"

# build docker image
docker build -t  $IMAGE_NAME .