#!/usr/bin/env bash
set -euo pipefail
EXT_DIR="${CODE_SERVER_EXTENSIONS:-/opt/code-server/extensions}"
LIST="${1:-/opt/vscode-cloud/extensions.txt}"
mkdir -p "$EXT_DIR"
export SERVICE_URL="${SERVICE_URL:-https://open-vsx.org/vscode/gallery}"
export ITEM_URL="${ITEM_URL:-https://open-vsx.org/vscode/item}"

required="Continue.continue"
code-server --install-extension "$required" --extensions-dir "$EXT_DIR" --force

while IFS= read -r ext || [ -n "$ext" ]; do
  ext="$(echo "$ext" | tr -d '\r' | sed 's/#.*//;s/[[:space:]]*$//')"
  [ -z "$ext" ] && continue
  [ "$ext" = "$required" ] && continue
  code-server --install-extension "$ext" --extensions-dir "$EXT_DIR" --force \
    || echo "optional extension failed: $ext"
done < "$LIST"
