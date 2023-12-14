#!/bin/bash

# Function to gracefully terminate processes
terminate_processes() {
    echo "Terminating processes..."
    pkill -P $$  # Kill child processes
    exit
}

# Trap Ctrl+C (SIGINT) signal to call the termination function
trap terminate_processes INT

# Start FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 3000 --workers 4 &

# Store PIDs of background processes
fastapi_pid=$!

# Start RabbitMQ consumers
for i in {1..4}; do
    python -u inference_workers/workers.py &
done

# Store PIDs of background processes
rabbitmq_pids=$(jobs -p)

# Wait for both processes to finish
wait

# Terminate processes on script exit
terminate_processes