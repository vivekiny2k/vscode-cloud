#!/usr/bin/env bash
set -euo pipefail

COMFY=/workspace/runpod-slim/ComfyUI
CN="$COMFY/custom_nodes/ComfyUI-ReActor"
PY=$(ps aux | awk '/python.*main.py/ && !/awk/ {print $11; exit}')
if [[ -z "${PY:-}" ]] || [[ ! -x "$PY" ]]; then
  if [[ -x /workspace/runpod-slim/venv/bin/python ]]; then
    PY=/workspace/runpod-slim/venv/bin/python
  else
    PY=python3
  fi
fi
echo "PYTHON $PY"
"$PY" -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda)"

if [[ ! -d "$CN/.git" ]]; then
  git clone --depth 1 https://github.com/Gourieff/ComfyUI-ReActor.git "$CN"
fi

# Official ReActor skips frames it flags as 18+. This pod already runs adult I2V,
# so process every frame instead of dropping them.
python3 - <<'PY'
from pathlib import Path
p = Path("/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI-ReActor/scripts/reactor_sfw.py")
text = p.read_text()
needle = "def nsfw_image(img_data, model_path: str):"
if "return False  # pod: do not skip frames" not in text:
    start = text.find(needle)
    if start < 0:
        raise SystemExit("nsfw_image not found")
    p.write_text(text[:start] + needle + "\n    return False  # pod: do not skip frames\n")
    print("patched reactor_sfw.py")
else:
    print("reactor_sfw.py already patched")
PY

mkdir -p "$COMFY/models/insightface/models" \
         "$COMFY/models/facerestore_models"

swap="$COMFY/models/insightface/inswapper_128.onnx"
if [[ ! -s "$swap" ]]; then
  echo "downloading inswapper_128.onnx"
  curl -L --retry 5 --retry-all-errors -o "$swap" \
    "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/inswapper_128.onnx"
fi

buf_zip=/tmp/buffalo_l.zip
buf_dir="$COMFY/models/insightface/models/buffalo_l"
if [[ ! -f "$buf_dir/det_10g.onnx" ]]; then
  echo "downloading buffalo_l"
  curl -L --retry 5 --retry-all-errors -o "$buf_zip" \
    "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/buffalo_l.zip"
  mkdir -p "$buf_dir"
  unzip -o "$buf_zip" -d "$buf_dir"
  # zip may contain a nested buffalo_l/ folder
  if [[ -d "$buf_dir/buffalo_l" ]]; then
    mv "$buf_dir/buffalo_l/"* "$buf_dir/" || true
    rmdir "$buf_dir/buffalo_l" || true
  fi
fi

gfp="$COMFY/models/facerestore_models/GFPGANv1.4.pth"
if [[ ! -s "$gfp" ]]; then
  echo "downloading GFPGANv1.4.pth"
  curl -L --retry 5 --retry-all-errors -o "$gfp" \
    "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/facerestore_models/GFPGANv1.4.pth"
fi

echo "pip installing ReActor deps"
cd "$CN"
"$PY" install.py

echo "launch cmdline:"
pgrep -af "main.py" || true
