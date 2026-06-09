#!/usr/bin/env bash
# Pull default Ollama models into the running container

set -euo pipefail

MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
CONTAINER="${OLLAMA_CONTAINER:-astraos-ollama}"

echo "Pulling model: $MODEL"
docker exec "$CONTAINER" ollama pull "$MODEL"

echo "Done."