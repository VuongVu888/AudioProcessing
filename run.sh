#!/bin/bash

docker build --platform=linux/amd64 -t vuongvu/audio-processing:v1 .
docker compose up -d