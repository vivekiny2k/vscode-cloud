import json
import urllib.request
import base64
from pathlib import Path

creds = json.loads(Path("/workspace/runpod-slim/ComfyUI/custom_nodes/comfyui_auth/credentials.json").read_text())
token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
headers = {"Authorization": f"Basic {token}"}


def get(path):
    req = urllib.request.Request("http://127.0.0.1:8188" + path, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=20).read())


for name in ["CLIPVisionEncode", "ImageScale", "ImageFromBatch", "CLIPVisionLoader", "Note"]:
    info = get("/object_info")
    if name not in info:
        print("MISSING", name)
        continue
    print("====", name)
    print(json.dumps(info[name].get("input", {}), indent=2)[:1800])
    print()
