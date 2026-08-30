BACKEND := "query-repair-backend"
FRONTENDDIR := "query-repair-frontend"
MODULEDIR := "query-repair-module"

# VENV to PATH
VENV_BIN := justfile_directory() / "venv/bin"
export PATH := VENV_BIN + ":" + env_var("PATH") 

# Automatically initialize venv if it doesn't exist
[private]
setup-venv:
    @if [ ! -d "venv" ]; then python3 -m venv venv; fi

# serve the demo webapp   
_default:
    @just serve

# install python and node dependencies
install-requirements: setup-venv
    pip install -r query-repair-backend/requirements.txt
    cd query-repair-frontend && npm install

# install query repair module
install-repair-module: setup-venv
    python -m pip install -e query-repair-module

# start frontends and backends
serve:
    #!/usr/bin/env bash
    if [[ ! -v DATASETS_DIR || ! -d "${DATASETS_DIR}" ]]; then
        echo "Need to set DATASET_DIR environment variable to absolute path of query-repair-backend/app/datasets"
        exit 1
    fi
    
    # Trap SIGINT (Ctrl+C) and SIGTERM, then kill all background processes started by this script
    trap 'kill $(jobs -p) 2>/dev/null' EXIT

    echo "Starting backend..."
    just backend &

    echo "Starting frontend..."
    just frontend &

    sleep 3
    echo "Opending page..."
    just open
    
    # Wait for all background jobs to finish
    wait

# Open webapp in browser
open:
    cd query-repair-frontend && npm run open

# Start the backend
backend:
    echo "Backend running..."
    cd query-repair-backend && fastapi dev
    sleep 5

# Helper recipe for the frontend
frontend:
    echo "Frontend running..."
    cd query-repair-frontend && npm run dev -- --port 3000
    sleep 5    

# start frontends and backends
serve-log:
    #!/usr/bin/env bash
    if [[ ! -v DATASETS_DIR || ! -d "${DATASETS_DIR}" ]]; then
        echo "Need to set DATASET_DIR environment variable to absolute path of query-repair-backend/app/datasets"
        exit 1
    fi
    
    # Trap SIGINT (Ctrl+C) and SIGTERM, then kill all background processes started by this script
    trap 'kill $(jobs -p) 2>/dev/null' EXIT

    echo "Starting backend..."
    cd query-repair-backend && fastapi dev > backend-log.txt &

    echo "Starting frontend..."
    cd query-repair-frontend && npm run dev -- --port 3000 > fontend-log.txt &

    sleep 3
    echo "Opending page..."
    just open
    
    # Wait for all background jobs to finish
    wait

