#!/bin/bash

SESSION_NAME="my_session"

# Check if the tmux session exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
    # Create a new tmux session and run the first set of commands
    tmux new-session -d -s $SESSION_NAME "bash -c 'python3 -m venv myenv; source myenv/bin/activate; pip install -r requirements.txt; bash start'"
else
    echo "Tmux session $SESSION_NAME already exists."
fi
