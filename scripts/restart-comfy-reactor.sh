#!/usr/bin/env bash
set -euo pipefail
cd /workspace/runpod-slim/ComfyUI
# Do not let start.sh's wait take over: relaunch ourselves.
pkill -f 'python main.py' || true
sleep 2
# If start.sh already spawned a replacement, leave it; otherwise start one.
if ! pgrep -f 'python main.py' >/dev/null; then
  nohup python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header > /tmp/comfy-restart.log 2>&1 &
  echo "started pid $!"
else
  echo "already running $(pgrep -af 'python main.py')"
fi
for i in $(seq 1 60); do
  if python3 - <<'PY'
import json, urllib.request, base64
from pathlib import Path
creds = json.loads(Path("/workspace/runpod-slim/ComfyUI/custom_nodes/comfyui_auth/credentials.json").read_text())
token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
req = urllib.request.Request("http://127.0.0.1:8188/object_info/ReActorFaceSwap", headers={"Authorization": f"Basic {token}"})
try:
    body = urllib.request.urlopen(req, timeout=5).read()
    print(body[:2500].decode())
    raise SystemExit(0)
except Exception as e:
    print("wait", type(e).__name__, e)
    raise SystemExit(1)
PY
  then
    echo READY
    exit 0
  fi
  sleep 3
done
echo "timeout; log:"
tail -80 /tmp/comfy-restart.log || true
ls -l /workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI-ReActor | head
exit 1
