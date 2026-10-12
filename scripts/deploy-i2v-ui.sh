#!/bin/bash
set -euo pipefail
DEST=/workspace/runpod-slim/ComfyUI/custom_nodes/i2v_simple_ui
COMFY=/workspace/runpod-slim/ComfyUI
mkdir -p "$DEST"
cp -f /tmp/i2v-ui/index.html /tmp/i2v-ui/__init__.py "$DEST/"
sed -i 's/\r$//' "$DEST/index.html" "$DEST/__init__.py" || true
cd "$COMFY"
pkill -f "/usr/bin/python3.12 main.py" || true
sleep 2
pkill -KILL -f "/usr/bin/python3.12 main.py" || true
sleep 1
nohup python3.12 main.py --listen 0.0.0.0 --port 8188 --enable-cors-header >/workspace/runpod-slim/comfyui.out 2>&1 &
echo "restarted pid $!"
for i in $(seq 1 60); do
  if python3 - <<'PY'
import json, urllib.request, base64
from pathlib import Path
creds = json.loads(Path("/workspace/runpod-slim/ComfyUI/custom_nodes/comfyui_auth/credentials.json").read_text())
token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
req = urllib.request.Request("http://127.0.0.1:8188/i2v", headers={"Authorization": f"Basic {token}", "Accept": "text/html"})
try:
    html = urllib.request.urlopen(req, timeout=5).read().decode("utf-8", "replace")
except Exception as exc:
    raise SystemExit(1)
print("page", "1 minute" in html, "concat" in html)
req2 = urllib.request.Request(
    "http://127.0.0.1:8188/i2v/concat",
    data=b"{}",
    method="POST",
    headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
)
try:
    urllib.request.urlopen(req2, timeout=5).read()
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", "replace")
    print("concat_status", exc.code, body[:200])
    raise SystemExit(0 if exc.code in (400, 200) else 1)
print("concat_unexpected_200")
PY
  then
    echo ready
    exit 0
  fi
  sleep 2
done
echo "ComfyUI did not become ready"
tail -n 40 /workspace/runpod-slim/comfyui.out || true
exit 1
