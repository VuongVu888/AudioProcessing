#!/bin/bash

ENV_VARS_SCRIPT="set_env_vars.sh"

# Function to gracefully terminate processes
terminate_processes() {
    echo "Terminating processes..."
    pkill -P $$  # Kill child processes
    tmux kill-session -t mysession  # Kill tmux session
    exit
}

# Trap Ctrl+C (SIGINT) signal to call the termination function
trap terminate_processes INT

# Start a tmux session named "mysession"
tmux new-session -d -s mysession "source $ENV_VARS_SCRIPT && uvicorn app.main:app --host 0.0.0.0 --port 3000 --workers 4"

# Store PID of FastAPI process
fastapi_pid=$!

# Split the tmux session into 4 panes and start RabbitMQ consumers in each pane
tmux split-window -t mysession:0.0 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"
tmux split-window -t mysession:0.1 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"
tmux split-window -t mysession:0.2 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"
tmux split-window -t mysession:0.3 "source $ENV_VARS_SCRIPT && python -u inference_workers/workers.py"

# Set focus on the first pane
tmux select-pane -t mysession:0.0

# Wait for all processes to finish
wait

# Terminate processes on script exit
terminate_processes
