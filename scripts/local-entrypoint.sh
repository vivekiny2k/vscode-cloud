#!/usr/bin/env bash
# Local/CPU compose entrypoint. Production pods inherit /start.sh instead.
set -euo pipefail
mkdir -p /workspace
/post_start.sh
touch /workspace/logs/code-server.log /workspace/logs/ollama.log
exec tail -F /workspace/logs/code-server.log /workspace/logs/ollama.log
