#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

# Start the FastAPI server with the unified API
uvicorn api.main:app --reload