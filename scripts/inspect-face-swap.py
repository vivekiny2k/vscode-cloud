import json
import urllib.request
import base64
from pathlib import Path

root = Path("/workspace/runpod-slim/ComfyUI")
creds_path = root / "custom_nodes/comfyui_auth/credentials.json"
headers = {}
if creds_path.exists():
    creds = json.loads(creds_path.read_text())
    token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}


def get(path):
    req = urllib.request.Request("http://127.0.0.1:8188" + path, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


print("==== custom_nodes ====")
cn = root / "custom_nodes"
if cn.exists():
    for p in sorted(cn.iterdir()):
        if p.name.startswith("."):
            continue
        print(p.name)

print("==== models of interest ====")
models = root / "models"
for sub in [
    "insightface",
    "insightface/models",
    "insightface/models/buffalo_l",
    "facerestore_models",
    "facedetection",
    "ultralytics",
    "ultralytics/bbox",
    "nsfw",
    "reactor",
]:
    d = models / sub if not str(sub).startswith("/") else Path(sub)
    print(f"-- {d} exists={d.exists()}")
    if d.exists() and d.is_dir():
        files = sorted(x for x in d.rglob("*") if x.is_file())[:40]
        for f in files:
            print(" ", f.relative_to(models), f.stat().st_size)

print("==== object_info match ====")
info = get("/object_info")
needles = (
    "face",
    "swap",
    "reactor",
    "insight",
    "vhs",
    "video",
    "animate",
    "pulid",
    "instantid",
    "ipadapter",
    "inpaint",
    "loadvideo",
    "videocombine",
    "vace",
    "phantom",
)
hits = []
for k in sorted(info):
    kl = k.lower()
    if any(n in kl for n in needles):
        hits.append(k)
        print("NODE", k)
print("HIT_COUNT", len(hits))

for k in [
    "ReActorFaceSwap",
    "ReActorFaceSwapOpt",
    "ReActorBuildFaceModel",
    "VHS_LoadVideo",
    "VHS_VideoCombine",
    "LoadVideo",
    "SaveVideo",
    "CreateVideo",
    "GetVideoComponents",
    "WanAnimateToVideo",
    "WanVaceToVideo",
]:
    print("HAS", k, k in info)
    if k in info:
        print(json.dumps(info[k].get("input", {}), indent=2)[:1800])
        print()
