#!/usr/bin/env bash
set -euo pipefail
COMFY=/workspace/runpod-slim/ComfyUI
CN="$COMFY/custom_nodes/ComfyUI-ReActor"
gfp="$COMFY/models/facerestore_models/GFPGANv1.4.pth"
mkdir -p "$COMFY/models/facerestore_models"
if [[ ! -s "$gfp" ]]; then
  echo "downloading GFPGANv1.4.pth"
  curl -L --retry 5 --retry-all-errors -o "$gfp" \
    "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/facerestore_models/GFPGANv1.4.pth"
fi
ls -lh "$gfp"
echo "==== processes ===="
ps aux | grep -E 'python|main.py' | grep -v grep
echo "==== pythons ===="
ls -l /workspace/runpod-slim/venv/bin/python 2>/dev/null || true
ls -l /usr/bin/python3
# Prefer the interpreter already running ComfyUI
PY=$(ps aux | awk '/[m]ain.py/ {print $11; exit}')
if [[ -z "${PY:-}" || ! -x "$PY" ]]; then
  PY=python3
fi
echo "PIP PYTHON $PY"
"$PY" -c "import sys; print(sys.executable); import torch; print(torch.__version__, torch.version.cuda)"
cd "$CN"
"$PY" install.py
echo "install.py done"
