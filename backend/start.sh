#!/bin/bash

# Print diagnostic startup headers
echo "Starting stateless multi-process backend services..."
echo "Database Host: $SUPABASE_DB_HOST"

# 1. Start the CubeJS Analytical Server in the background on port 4000
echo "Launching private CubeJS Analytical Server..."
cubejs-server &

# Wait 6 seconds to ensure the analytical layer finishes compilation & handshakes with Supabase
sleep 6

# 2. Start the Python FastAPI Gateway in the foreground on port 7860 (Hugging Face default)
echo "Launching public FastAPI gateway on port 7860..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 7860 --app-dir src