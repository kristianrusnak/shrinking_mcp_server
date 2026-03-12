#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "Building Docker image: shrinking-algorithm-mcp..."
docker build -f mcp_server/Dockerfile -t shrinking-algorithm-mcp .
echo "Build complete."