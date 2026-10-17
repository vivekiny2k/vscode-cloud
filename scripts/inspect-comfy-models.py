import json
import urllib.request
import base64
from pathlib import Path

creds_path = Path("/workspace/runpod-slim/ComfyUI/custom_nodes/comfyui_auth/credentials.json")
if creds_path.exists():
    creds = json.loads(creds_path.read_text())
    token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
else:
    headers = {}


def get(path):
    req = urllib.request.Request("http://127.0.0.1:8188" + path, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


print("AUTH", bool(creds_path.exists()))
try:
    stats = get("/system_stats")
    print("SYSTEM", json.dumps(stats, indent=2)[:1500])
except Exception as exc:
    print("SYSTEM_ERR", type(exc).__name__, exc)

root = Path("/workspace/runpod-slim/ComfyUI/models")
for sub in [
    "diffusion_models",
    "checkpoints",
    "loras",
    "vae",
    "text_encoders",
    "clip_vision",
    "clip",
    "unet",
    "controlnet",
    "ipadapter",
    "insightface",
]:
    d = root / sub
    print(f"==== {sub} ====")
    if not d.exists():
        print("(missing)")
        continue
    files = sorted(p.name for p in d.rglob("*") if p.is_file() and p.suffix.lower() in {".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".onnx"})
    for name in files[:80]:
        print(name)
    if not files:
        print("(empty)")

info = get("/object_info")
keys = [
    "WanImageToVideo",
    "WanFirstLastFrameToVideo",
    "WanPhantomSubjectToVideo",
    "WanFunControlToVideo",
    "Wan22ImageToVideoLatent",
    "ImageStitch",
    "ImageComposite",
    "ImageCompositeMasked",
    "ImageConcatFromBatch",
    "ImageConcatMulti",
    "LoadImage",
]
print("==== nodes ====")
for k in keys:
    print(k, "YES" if k in info else "no")

print("==== flf inputs ====")
if "WanFirstLastFrameToVideo" in info:
    print(json.dumps(info["WanFirstLastFrameToVideo"].get("input", {}), indent=2)[:3000])

print("==== stitch inputs ====")
if "ImageStitch" in info:
    print(json.dumps(info["ImageStitch"].get("input", {}), indent=2)[:1500])
if "ImageConcatMulti" in info:
    print("ImageConcatMulti", json.dumps(info["ImageConcatMulti"].get("input", {}), indent=2)[:1500])
