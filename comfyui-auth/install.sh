#!/bin/bash
# Run on the ComfyUI pod after you upload this folder. Does not start a pod.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
COMFY="${COMFY:-/workspace/runpod-slim/ComfyUI}"
DEST="$COMFY/custom_nodes/comfyui_auth"
FB_DB="${FB_DB:-/workspace/runpod-slim/filebrowser.db}"

python3 - <<PY
import json
from pathlib import Path
creds = json.loads(Path("$SRC/credentials.json").read_text())
assert creds.get("username") == "admin", "username must be admin"
assert creds.get("password"), "password missing"
print("creds_ok")
PY

USER="$(python3 -c 'import json; print(json.load(open("'"$SRC"'/credentials.json"))["username"])')"
PASS="$(python3 -c 'import json; print(json.load(open("'"$SRC"'/credentials.json"))["password"])')"

mkdir -p "$DEST"
cp -f "$SRC/__init__.py" "$SRC/login.html" "$SRC/credentials.json" "$DEST/"
sed -i 's/\r$//' "$DEST/__init__.py" "$DEST/login.html" || true

if [ ! -f "$FB_DB" ]; then
  echo "FileBrowser db not found at $FB_DB"
  exit 1
fi

pkill -TERM -x filebrowser || true
sleep 1
pkill -KILL -x filebrowser || true
if ! filebrowser users update "$USER" --password "$PASS" -d "$FB_DB"; then
  echo "FileBrowser password update failed"
  exit 1
fi
filebrowser users update "$USER" \
  --perm.admin \
  --perm.create \
  --perm.delete \
  --perm.download \
  --perm.modify \
  --perm.rename \
  --perm.share \
  -d "$FB_DB" >/dev/null || true
BRAND="${BRAND:-/workspace/runpod-slim/filebrowser-branding}"
mkdir -p "$BRAND"
if [ -f "$SRC/../filebrowser-branding/custom.css" ]; then
  cp -f "$SRC/../filebrowser-branding/custom.css" "$BRAND/custom.css"
  sed -i 's/\r$//' "$BRAND/custom.css" || true
fi
filebrowser config set --address 0.0.0.0 -d "$FB_DB" >/dev/null
filebrowser config set --port 8080 -d "$FB_DB" >/dev/null
filebrowser config set --root /workspace -d "$FB_DB" >/dev/null
filebrowser config set --branding.files "$BRAND" -d "$FB_DB" >/dev/null
filebrowser config set --singleClick=false -d "$FB_DB" >/dev/null || true
nohup filebrowser -d "$FB_DB" >/filebrowser.log 2>&1 &
echo "filebrowser_updated"

echo
echo "Auth files are in $DEST"
echo "FileBrowser user $USER now uses the same password."
echo "Restart ComfyUI so the login page loads (do not recreate the pod unless you mean to)."
echo "Set JUPYTER_PASSWORD to the same password on pod create if Jupyter should match."
