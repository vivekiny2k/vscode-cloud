"""UI-format ReActor video face-swap: LoadVideo + face photo -> swapped video."""
import json
from pathlib import Path

OUT = Path(__file__).with_name("face-swap-video.json")

link_id = 0
links = []


def L(origin, oslot, target, tslot, typ):
    global link_id
    link_id += 1
    links.append([link_id, origin, oslot, target, tslot, typ])
    return link_id


def inp(name, typ, link=None, widget=None, shape=None):
    d = {"name": name, "type": typ, "link": link}
    if widget:
        d["widget"] = {"name": widget}
    if shape is not None:
        d["shape"] = shape
    return d


def out(name, typ, out_links=None, slot=0):
    return {"name": name, "type": typ, "slot_index": slot, "links": out_links}


def node(nid, ntype, pos, size, inputs, outputs, widgets=None, title=None, order=0):
    n = {
        "id": nid,
        "type": ntype,
        "pos": pos,
        "size": size,
        "flags": {},
        "order": order,
        "mode": 0,
        "inputs": inputs,
        "outputs": outputs,
        "properties": {"Node name for S&R": ntype, "cnr_id": "comfy-core"},
        "widgets_values": widgets if widgets is not None else [],
    }
    if title:
        n["title"] = title
    return n


vid = L(1, 0, 2, 0, "VIDEO")
frames = L(2, 0, 4, 0, "IMAGE")
audio = L(2, 1, 5, 2, "AUDIO")
fps = L(2, 2, 5, 1, "FLOAT")
face = L(3, 0, 4, 1, "IMAGE")
swapped = L(4, 0, 5, 0, "IMAGE")
video_out = L(5, 0, 6, 0, "VIDEO")

nodes = [
    node(
        7,
        "MarkdownNote",
        [-40, -280],
        [620, 220],
        [],
        [],
        [
            "## Video face swap (ReActor)\n\n"
            "1. **Target video** — the clip whose face(s) you want replaced.\n"
            "2. **New face** — a clear photo of the replacement face, looking toward camera.\n"
            "3. If several faces are in the video, set **input face index** (0 is the largest).\n"
            "4. **Run**. Output is `video/faceswap`.\n\n"
            "Long clips are slower (every frame is swapped). GFPGAN restore is off by default for speed; pick it on the ReActor node if you want a cleaner face."
        ],
        title="How to use",
        order=0,
    ),
    node(
        1,
        "LoadVideo",
        [0, 0],
        [320, 250],
        [],
        [out("VIDEO", "VIDEO", [vid], 0)],
        [""],
        title="Target video",
        order=1,
    ),
    node(
        2,
        "GetVideoComponents",
        [360, 40],
        [240, 80],
        [inp("video", "VIDEO", vid)],
        [
            out("images", "IMAGE", [frames], 0),
            out("audio", "AUDIO", [audio], 1),
            out("fps", "FLOAT", [fps], 2),
        ],
        [],
        title="Split into frames",
        order=2,
    ),
    node(
        3,
        "LoadImage",
        [0, 320],
        [360, 420],
        [],
        [out("IMAGE", "IMAGE", [face], 0), out("MASK", "MASK", None, 1)],
        ["", "image"],
        title="New face",
        order=3,
    ),
    node(
        4,
        "ReActorFaceSwap",
        [700, 40],
        [360, 430],
        [
            inp("input_image", "IMAGE", frames),
            inp("source_image", "IMAGE", face, shape=7),
            inp("face_model", "FACE_MODEL", None, shape=7),
            inp("face_boost", "FACE_BOOST", None, shape=7),
        ],
        [
            out("SWAPPED_IMAGE", "IMAGE", [swapped], 0),
            out("FACE_MODEL", "FACE_MODEL", None, 1),
            out("ORIGINAL_IMAGE", "IMAGE", None, 2),
        ],
        [
            True,
            "inswapper_128.onnx",
            "retinaface_resnet50",
            "none",
            1,
            0.5,
            "no",
            "no",
            "0",
            "0",
            1,
        ],
        title="Swap face",
        order=4,
    ),
    node(
        5,
        "CreateVideo",
        [1120, 40],
        [250, 120],
        [
            inp("images", "IMAGE", swapped),
            inp("fps", "FLOAT", fps, widget="fps"),
            inp("audio", "AUDIO", audio, shape=7),
        ],
        [out("VIDEO", "VIDEO", [video_out], 0)],
        [16],
        title="Rebuild video",
        order=5,
    ),
    node(
        6,
        "SaveVideo",
        [1420, 40],
        [280, 130],
        [inp("video", "VIDEO", video_out)],
        [],
        ["video/faceswap", "auto", "auto"],
        title="Save",
        order=6,
    ),
]

wf = {
    "id": "face-swap-video",
    "revision": 0,
    "last_node_id": 7,
    "last_link_id": link_id,
    "nodes": nodes,
    "links": links,
    "groups": [
        {"id": 1, "title": "1. Inputs", "bounding": [-20, -40, 640, 800], "color": "#3f789e", "font_size": 24, "flags": {}},
        {"id": 2, "title": "2. Swap and save", "bounding": [680, -40, 1060, 540], "color": "#3f789e", "font_size": 24, "flags": {}},
    ],
    "config": {},
    "extra": {"ds": {"scale": 0.7, "offset": [80, 360]}, "frontendVersion": "1.47.10"},
    "version": 0.4,
}

# Link sanity
ids = {n["id"] for n in nodes}
link_map = {item[0]: item for item in links}
for n in nodes:
    for i in n.get("inputs", []):
        lid = i.get("link")
        if not lid:
            continue
        item = link_map[lid]
        if item[3] != n["id"]:
            raise SystemExit(f"link {lid} target mismatch on {n['id']}")
        if item[5] != i["type"]:
            raise SystemExit(f"link {lid} type {item[5]} vs {i['type']} on {n['id']} {i['name']}")

OUT.write_text(json.dumps(wf, indent=2), encoding="utf-8")
print("wrote", OUT, "links", links)
