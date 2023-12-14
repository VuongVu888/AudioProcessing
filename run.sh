#!/bin/bash

# Start FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 3000 --workers 4 &

# Start RabbitMQ consumers
for i in {1..4}; do
    python -u inference_workers/workers.py &
done

# Wait for both processes to finish
wait