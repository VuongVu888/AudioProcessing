#!/bin/bash

ENV_VARS_SCRIPT="set_env_vars.sh"

# Function to gracefully terminate processes
terminate_processes() {
    echo "Terminating processes..."
    pkill -P $$  # Kill child processes
    exit
}

# Trap Ctrl+C (SIGINT) signal to call the termination function
trap terminate_processes INT

# Start a tmux session named "mysession"
tmux new-session -d -s fastapi "source $ENV_VARS_SCRIPT && uvicorn app.main:app --host 0.0.0.0 --port 3000 --workers 4"

# Store PID of FastAPI process
fastapi_pid=$!

# Split the tmux session into 4 panes and start RabbitMQ consumers in each pane
tmux new-session -d -s consumer1 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"
tmux new-session -d -s consumer2 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"
tmux new-session -d -s consumer3 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"
tmux new-session -d -s consumer4 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"

# Wait for all processes to finish
wait

# Terminate processes on script exit
terminate_processes
