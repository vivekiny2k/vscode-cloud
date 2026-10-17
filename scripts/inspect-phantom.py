import json, urllib.request, base64
from pathlib import Path
creds = json.loads(Path("/workspace/runpod-slim/ComfyUI/custom_nodes/comfyui_auth/credentials.json").read_text())
token = base64.b64encode(f"{creds['username']}:{creds['password']}".encode()).decode()
req = urllib.request.Request("http://127.0.0.1:8188/object_info", headers={"Authorization": f"Basic {token}"})
info = json.loads(urllib.request.urlopen(req, timeout=30).read())
for k in sorted(info):
    if "Phantom" in k or "FLF" in k or "FirstLast" in k or "Subject" in k:
        print("NODE", k)
        print(json.dumps(info[k].get("input", {}), indent=2)[:2500])
        print()
# templates endpoint
for path in ["/templates", "/api/userdata/templates", "/object_info/WanFirstLastFrameToVideo"]:
    try:
        r = urllib.request.Request("http://127.0.0.1:8188" + path, headers={"Authorization": f"Basic {token}"})
        body = urllib.request.urlopen(r, timeout=10).read()[:500]
        print("PATH", path, body[:200])
    except Exception as e:
        print("PATH", path, type(e).__name__, e)
