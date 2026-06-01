#!/bin/bash

# Print diagnostic startup headers
echo "Starting stateless multi-process backend services..."
echo "Database Host: $SUPABASE_DB_HOST"

# Export CubeJS environment variables using our Supabase secrets
export CUBEJS_DB_TYPE=postgres
export CUBEJS_DB_HOST=$SUPABASE_DB_HOST
export CUBEJS_DB_NAME=$SUPABASE_DB_NAME
export CUBEJS_DB_USER=$SUPABASE_DB_USER
export CUBEJS_DB_PASS=$SUPABASE_DB_PASS
export CUBEJS_DB_PORT=$SUPABASE_DB_PORT
export CUBEJS_DB_SSL=true
export CUBEJS_DEV_MODE=true

# 1. Start the CubeJS Analytical Server in the background on port 4000
echo "Launching private CubeJS Analytical Server..."
/cube/node_modules/.bin/cubejs-server &

# Wait 8 seconds to ensure the analytical layer finishes compilation & handshakes with Supabase
sleep 8

# 2. Start the Python FastAPI Gateway in the foreground on port 7860 (Hugging Face default)
echo "Launching public FastAPI gateway on port 7860..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 7860 --app-dir src