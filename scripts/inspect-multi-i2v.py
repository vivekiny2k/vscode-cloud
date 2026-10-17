import json
import urllib.request
import base64
from pathlib import Path

root = Path("/workspace/runpod-slim/ComfyUI")
creds = json.loads((root / "custom_nodes/comfyui_auth/credentials.json").read_text())
token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
headers = {"Authorization": f"Basic {token}"}


def get(path):
    req = urllib.request.Request("http://127.0.0.1:8188" + path, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


info = get("/object_info")
keys = [
    "WanFirstLastFrameToVideo",
    "WanImageToVideo",
    "ImageStitch",
    "ImageConcatFromBatch",
    "ImageConcatMulti",
    "ImageBatch",
    "BatchImages",
    "GetImageSize",
    "CreateVideo",
    "SaveVideo",
    "LoadVideo",
    "GetVideoComponents",
    "ReplaceVideoLatentFrames",
    "Wan22ImageToVideoLatent",
    "ImageResizeKJv2",
    "ImageResize+",
    "ImageScale",
    "MarkdownNote",
]
print("==== has ====")
for k in keys:
    print(k, "YES" if k in info else "no")

needles = ("concat", "stitch", "batch", "flf", "firstlast", "middle", "keyframe")
print("==== name hits ====")
for k in sorted(info):
    kl = k.lower()
    if any(n in kl for n in needles):
        print(k)

print("==== WanFirstLastFrameToVideo ====")
if "WanFirstLastFrameToVideo" in info:
    print(json.dumps(info["WanFirstLastFrameToVideo"], indent=2)[:4000])

print("==== ImageBatch ====")
for k in info:
    if "imagebatch" in k.lower() or k in ("ImageBatch", "BatchImages", "ImageFromBatch"):
        print(k, json.dumps(info[k].get("input", {}), indent=2)[:1200])

print("==== concat/video ====")
for k in info:
    kl = k.lower()
    if "video" in kl and ("concat" in kl or "combine" in kl or "join" in kl or "merge" in kl or "stitch" in kl):
        print(k, json.dumps(info[k].get("input", {}), indent=2)[:1500])
