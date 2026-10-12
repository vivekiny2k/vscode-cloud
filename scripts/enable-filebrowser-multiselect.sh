#!/bin/bash
# Stop FileBrowser, grant delete/download, install branding, restart.
set -euo pipefail
FB_DB="${FB_DB:-/workspace/runpod-slim/filebrowser.db}"
BRAND="${BRAND:-/workspace/runpod-slim/filebrowser-branding}"

mkdir -p "$BRAND"
cp -f /tmp/filebrowser-branding/custom.css "$BRAND/custom.css"
sed -i 's/\r$//' "$BRAND/custom.css" || true

pkill -TERM -x filebrowser || true
sleep 1
pkill -KILL -x filebrowser || true
sleep 1

echo "---- users before ----"
filebrowser users ls -d "$FB_DB" || true

filebrowser users update admin \
  --perm.admin \
  --perm.create \
  --perm.delete \
  --perm.download \
  --perm.modify \
  --perm.rename \
  --perm.share \
  -d "$FB_DB"

filebrowser config set --singleClick=false -d "$FB_DB" >/dev/null || true
filebrowser config set --branding.files "$BRAND" -d "$FB_DB" >/dev/null
filebrowser config set --address 0.0.0.0 -d "$FB_DB" >/dev/null
filebrowser config set --port 8080 -d "$FB_DB" >/dev/null
filebrowser config set --root /workspace -d "$FB_DB" >/dev/null

echo "---- users after ----"
filebrowser users ls -d "$FB_DB" || true

nohup filebrowser -d "$FB_DB" >/filebrowser.log 2>&1 &
sleep 1
ss -ltnp | grep 8080 || true
echo filebrowser_multiselect_ready
