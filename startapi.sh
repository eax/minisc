#!/bin/bash

# Navigate to the directory containing the FastAPI application
cd "$(dirname "$0")/azure/src/api"

# Start the FastAPI server
uvicorn main:app --reload