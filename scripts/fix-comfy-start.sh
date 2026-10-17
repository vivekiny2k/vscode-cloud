#!/usr/bin/env bash
set -euo pipefail
echo "PATH=$PATH"
which python python3 || true
pgrep -af main.py || echo "no main.py"
echo "==== log ===="
tail -100 /tmp/comfy-restart.log || echo "no restart log"
echo "==== start.sh ===="
head -80 /workspace/runpod-slim/start.sh || true
ls /workspace/runpod-slim/*.sh | head
echo "==== retry with python3 ===="
cd /workspace/runpod-slim/ComfyUI
pkill -f 'python.*main.py' || true
sleep 1
nohup python3 main.py --listen 0.0.0.0 --port 8188 --enable-cors-header > /tmp/comfy-restart.log 2>&1 &
echo started $!
sleep 8
tail -50 /tmp/comfy-restart.log
pgrep -af main.py || true
ss -lntp | grep 8188 || netstat -lntp | grep 8188 || true
