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

if filebrowser users update "$USER" --password "$PASS" -d "$FB_DB"; then
  echo "filebrowser_updated"
elif filebrowser users update "$USER" -p "$PASS" -d "$FB_DB"; then
  echo "filebrowser_updated"
else
  echo "FileBrowser password update failed"
  exit 1
fi

echo
echo "Auth files are in $DEST"
echo "FileBrowser user $USER now uses the same password."
echo "Restart ComfyUI so the login page loads (do not recreate the pod unless you mean to)."
echo "Jupyter still uses JUPYTER_PASSWORD until you set that env to the same password on the next start."
