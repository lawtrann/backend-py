#!/usr/bin/env bash
# Launch or attach to the "backend" tmux dev session.
set -euo pipefail

SESSION="backend"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Session '$SESSION' already exists. Attaching..."
    tmux attach-session -t "$SESSION"
    exit 0
fi

tmux new-session -d -s "$SESSION" -n "dev" -x 220 -y 50

# Pane 1 (top-left, main): Docker DB + live logs
tmux send-keys -t "$SESSION:dev.0" "cd '$BACKEND_DIR'" Enter
tmux send-keys -t "$SESSION:dev.0" "docker compose up -d db minio && docker compose logs -f db minio" Enter

# Split right → pane 2 (top-right): FastAPI dev server
tmux split-window -t "$SESSION:dev.0" -h -p 50
tmux send-keys -t "$SESSION:dev.1" "cd '$BACKEND_DIR'" Enter
tmux send-keys -t "$SESSION:dev.1" "uv run fastapi dev app/main.py" Enter

# Split pane 2 → pane 3 (bottom-right): shell
tmux split-window -t "$SESSION:dev.1" -v -p 40
tmux send-keys -t "$SESSION:dev.2" "cd '$BACKEND_DIR'" Enter

tmux select-pane -t "$SESSION:dev.0"
tmux attach-session -t "$SESSION"
