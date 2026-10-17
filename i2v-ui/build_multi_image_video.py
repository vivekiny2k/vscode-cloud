"""Build a UI-format Wan 2.2 Lightning storyboard: 4 photos + prompt -> video."""
import json
from pathlib import Path

OUT = Path(__file__).with_name("multi-image-video.json")

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
    return {
        "name": name,
        "type": typ,
        "slot_index": slot,
        "links": out_links,
    }


def node(
    nid,
    ntype,
    pos,
    size,
    inputs,
    outputs,
    widgets=None,
    title=None,
    order=0,
    color=None,
):
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
    if color:
        n["color"] = color
        n["bgcolor"] = "#000"
    return n


# Shared models
c_clip = L(1, 0, 9, 0, "CLIP")
c_clip_n = L(1, 0, 10, 0, "CLIP")
c_uh = L(2, 0, 4, 0, "MODEL")
c_ul = L(3, 0, 5, 0, "MODEL")
c_lh = L(4, 0, 6, 0, "MODEL")
c_ll = L(5, 0, 7, 0, "MODEL")

# CLIP vision encodes
cv1 = L(19, 0, 71, 0, "CLIP_VISION")
cv2 = L(19, 0, 72, 0, "CLIP_VISION")
cv3 = L(19, 0, 73, 0, "CLIP_VISION")
cv4 = L(19, 0, 74, 0, "CLIP_VISION")
img1 = L(11, 0, 15, 0, "IMAGE")
img2 = L(12, 0, 16, 0, "IMAGE")
img3 = L(13, 0, 17, 0, "IMAGE")
img4 = L(14, 0, 18, 0, "IMAGE")
# scale -> clip vision encode image
s1cv = L(15, 0, 71, 1, "IMAGE")
s2cv = L(16, 0, 72, 1, "IMAGE")
s3cv = L(17, 0, 73, 1, "IMAGE")
s4cv = L(18, 0, 74, 1, "IMAGE")

# Segment A: 1 -> 2
a_pos = L(9, 0, 20, 0, "CONDITIONING")
a_neg = L(10, 0, 20, 1, "CONDITIONING")
a_vae = L(8, 0, 20, 2, "VAE")
a_cvs = L(71, 0, 20, 3, "CLIP_VISION_OUTPUT")
a_cve = L(72, 0, 20, 4, "CLIP_VISION_OUTPUT")
a_st = L(15, 0, 20, 5, "IMAGE")
a_en = L(16, 0, 20, 6, "IMAGE")
a_mh = L(6, 0, 21, 0, "MODEL")
a_ph = L(20, 0, 21, 1, "CONDITIONING")
a_nh = L(20, 1, 21, 2, "CONDITIONING")
a_lh = L(20, 2, 21, 3, "LATENT")
a_ml = L(7, 0, 22, 0, "MODEL")
a_pl = L(20, 0, 22, 1, "CONDITIONING")
a_nl = L(20, 1, 22, 2, "CONDITIONING")
a_llat = L(21, 0, 22, 3, "LATENT")
a_dec_s = L(22, 0, 23, 0, "LATENT")
a_dec_v = L(8, 0, 23, 1, "VAE")

# Segment B: 2 -> 3
b_pos = L(9, 0, 30, 0, "CONDITIONING")
b_neg = L(10, 0, 30, 1, "CONDITIONING")
b_vae = L(8, 0, 30, 2, "VAE")
b_cvs = L(72, 0, 30, 3, "CLIP_VISION_OUTPUT")
b_cve = L(73, 0, 30, 4, "CLIP_VISION_OUTPUT")
b_st = L(16, 0, 30, 5, "IMAGE")
b_en = L(17, 0, 30, 6, "IMAGE")
b_mh = L(6, 0, 31, 0, "MODEL")
b_ph = L(30, 0, 31, 1, "CONDITIONING")
b_nh = L(30, 1, 31, 2, "CONDITIONING")
b_lh = L(30, 2, 31, 3, "LATENT")
b_ml = L(7, 0, 32, 0, "MODEL")
b_pl = L(30, 0, 32, 1, "CONDITIONING")
b_nl = L(30, 1, 32, 2, "CONDITIONING")
b_llat = L(31, 0, 32, 3, "LATENT")
b_dec_s = L(32, 0, 33, 0, "LATENT")
b_dec_v = L(8, 0, 33, 1, "VAE")

# Segment C: 3 -> 4
c_pos = L(9, 0, 40, 0, "CONDITIONING")
c_neg = L(10, 0, 40, 1, "CONDITIONING")
c_vae = L(8, 0, 40, 2, "VAE")
c_cvs = L(73, 0, 40, 3, "CLIP_VISION_OUTPUT")
c_cve = L(74, 0, 40, 4, "CLIP_VISION_OUTPUT")
c_st = L(17, 0, 40, 5, "IMAGE")
c_en = L(18, 0, 40, 6, "IMAGE")
c_mh = L(6, 0, 41, 0, "MODEL")
c_ph = L(40, 0, 41, 1, "CONDITIONING")
c_nh = L(40, 1, 41, 2, "CONDITIONING")
c_lat = L(40, 2, 41, 3, "LATENT")
c_ml = L(7, 0, 42, 0, "MODEL")
c_pl = L(40, 0, 42, 1, "CONDITIONING")
c_nl = L(40, 1, 42, 2, "CONDITIONING")
c_llat = L(41, 0, 42, 3, "LATENT")
c_dec_s = L(42, 0, 43, 0, "LATENT")
c_dec_v = L(8, 0, 43, 1, "VAE")

# Stitch frames (drop first frame of later clips so the keyframe is not doubled)
skip_b = L(33, 0, 50, 0, "IMAGE")
skip_c = L(43, 0, 51, 0, "IMAGE")
join_ab1 = L(23, 0, 52, 0, "IMAGE")
join_ab2 = L(50, 0, 52, 1, "IMAGE")
join_abc1 = L(52, 0, 53, 0, "IMAGE")
join_abc2 = L(51, 0, 53, 1, "IMAGE")
to_vid = L(53, 0, 54, 0, "IMAGE")
to_save = L(54, 0, 55, 0, "VIDEO")

NEG = (
    "blurry, jitter, morphing identity, extra fingers, still photo, "
    "watermark, subtitles, text, worst quality, low quality"
)
POS = (
    "smooth cinematic motion connecting these photos, people stay recognizable, "
    "natural lighting, camera follows the action"
)

ks_high = ["enable", 42, "randomize", 4, 1, "euler", "simple", 0, 2, "enable"]
ks_low = ["disable", 0, "fixed", 4, 1, "euler", "simple", 2, 10000, "disable"]
scale_w = ["bicubic", 832, 480, "center"]
flf_w = [832, 480, 81, 1]

nodes = [
    node(
        56,
        "MarkdownNote",
        [-520, -520],
        [480, 280],
        [],
        [],
        [
            "## Multi-image storyboard (Wan 2.2 Lightning)\n\n"
            "1. Drop photos on **Image 1 to Image 4** in story order.\n"
            "   Only have 2 photos? Duplicate them: 1=start, 2=start, 3=end, 4=end.\n"
            "2. Type what should happen in **Instructions**.\n"
            "3. **Run**. Three 5s clips are stitched (~15s at 16fps).\n\n"
            "This is first-last-frame interpolation, not a collage. "
            "The model moves FROM one photo TOWARD the next while following the prompt."
        ],
        title="How to use",
        order=0,
    ),
    node(1, "CLIPLoader", [40, -70], [320, 110], [], [out("CLIP", "CLIP", [c_clip, c_clip_n], 0)], ["umt5_xxl_fp8_e4m3fn_scaled.safetensors", "wan", "default"], title="Text encoder", order=1),
    node(2, "UNETLoader", [40, 70], [370, 90], [], [out("MODEL", "MODEL", [c_uh], 0)], ["wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors", "default"], title="High noise", order=2),
    node(3, "UNETLoader", [40, 190], [370, 90], [], [out("MODEL", "MODEL", [c_ul], 0)], ["wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors", "default"], title="Low noise", order=3),
    node(4, "LoraLoaderModelOnly", [450, 70], [380, 90], [inp("model", "MODEL", c_uh)], [out("MODEL", "MODEL", [c_lh], 0)], ["wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", 1], title="Lightning high", order=4),
    node(5, "LoraLoaderModelOnly", [450, 190], [380, 90], [inp("model", "MODEL", c_ul)], [out("MODEL", "MODEL", [c_ll], 0)], ["wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors", 1], title="Lightning low", order=5),
    node(6, "ModelSamplingSD3", [870, 70], [210, 60], [inp("model", "MODEL", c_lh)], [out("MODEL", "MODEL", [a_mh, b_mh, c_mh], 0)], [5], order=6),
    node(7, "ModelSamplingSD3", [870, 190], [210, 60], [inp("model", "MODEL", c_ll)], [out("MODEL", "MODEL", [a_ml, b_ml, c_ml], 0)], [5], order=7),
    node(8, "VAELoader", [40, 310], [320, 60], [], [out("VAE", "VAE", [a_vae, a_dec_v, b_vae, b_dec_v, c_vae, c_dec_v], 0)], ["wan_2.1_vae.safetensors"], order=8),
    node(19, "CLIPVisionLoader", [40, 400], [320, 60], [], [out("CLIP_VISION", "CLIP_VISION", [cv1, cv2, cv3, cv4], 0)], ["clip_vision_h.safetensors"], order=9),
    node(
        9,
        "CLIPTextEncode",
        [450, 310],
        [430, 200],
        [inp("clip", "CLIP", c_clip)],
        [out("CONDITIONING", "CONDITIONING", [a_pos, b_pos, c_pos], 0)],
        [POS],
        title="Instructions (prompt)",
        order=10,
    ),
    node(
        10,
        "CLIPTextEncode",
        [450, 540],
        [430, 150],
        [inp("clip", "CLIP", c_clip_n)],
        [out("CONDITIONING", "CONDITIONING", [a_neg, b_neg, c_neg], 0)],
        [NEG],
        title="Negative",
        order=11,
    ),
    node(11, "LoadImage", [-520, -200], [360, 420], [], [out("IMAGE", "IMAGE", [img1], 0), out("MASK", "MASK", None, 1)], ["", "image"], title="Image 1 (start)", order=12),
    node(12, "LoadImage", [-520, 260], [360, 420], [], [out("IMAGE", "IMAGE", [img2], 0), out("MASK", "MASK", None, 1)], ["", "image"], title="Image 2", order=13),
    node(13, "LoadImage", [-520, 720], [360, 420], [], [out("IMAGE", "IMAGE", [img3], 0), out("MASK", "MASK", None, 1)], ["", "image"], title="Image 3", order=14),
    node(14, "LoadImage", [-520, 1180], [360, 420], [], [out("IMAGE", "IMAGE", [img4], 0), out("MASK", "MASK", None, 1)], ["", "image"], title="Image 4 (end)", order=15),
    node(15, "ImageScale", [-120, -80], [270, 130], [inp("image", "IMAGE", img1)], [out("IMAGE", "IMAGE", [s1cv, a_st], 0)], scale_w, title="Resize 1", order=16),
    node(16, "ImageScale", [-120, 380], [270, 130], [inp("image", "IMAGE", img2)], [out("IMAGE", "IMAGE", [s2cv, a_en, b_st], 0)], scale_w, title="Resize 2", order=17),
    node(17, "ImageScale", [-120, 840], [270, 130], [inp("image", "IMAGE", img3)], [out("IMAGE", "IMAGE", [s3cv, b_en, c_st], 0)], scale_w, title="Resize 3", order=18),
    node(18, "ImageScale", [-120, 1300], [270, 130], [inp("image", "IMAGE", img4)], [out("IMAGE", "IMAGE", [s4cv, c_en], 0)], scale_w, title="Resize 4", order=19),
    node(71, "CLIPVisionEncode", [180, 500], [250, 80], [inp("clip_vision", "CLIP_VISION", cv1), inp("image", "IMAGE", s1cv)], [out("CLIP_VISION_OUTPUT", "CLIP_VISION_OUTPUT", [a_cvs], 0)], ["center"], title="Vision 1", order=20),
    node(72, "CLIPVisionEncode", [180, 610], [250, 80], [inp("clip_vision", "CLIP_VISION", cv2), inp("image", "IMAGE", s2cv)], [out("CLIP_VISION_OUTPUT", "CLIP_VISION_OUTPUT", [a_cve, b_cvs], 0)], ["center"], title="Vision 2", order=21),
    node(73, "CLIPVisionEncode", [180, 720], [250, 80], [inp("clip_vision", "CLIP_VISION", cv3), inp("image", "IMAGE", s3cv)], [out("CLIP_VISION_OUTPUT", "CLIP_VISION_OUTPUT", [b_cve, c_cvs], 0)], ["center"], title="Vision 3", order=22),
    node(74, "CLIPVisionEncode", [180, 830], [250, 80], [inp("clip_vision", "CLIP_VISION", cv4), inp("image", "IMAGE", s4cv)], [out("CLIP_VISION_OUTPUT", "CLIP_VISION_OUTPUT", [c_cve], 0)], ["center"], title="Vision 4", order=23),
]

flf_inputs = lambda pos, neg, vae, cvs, cve, st, en: [
    inp("positive", "CONDITIONING", pos),
    inp("negative", "CONDITIONING", neg),
    inp("vae", "VAE", vae),
    inp("clip_vision_start_image", "CLIP_VISION_OUTPUT", cvs, shape=7),
    inp("clip_vision_end_image", "CLIP_VISION_OUTPUT", cve, shape=7),
    inp("start_image", "IMAGE", st, shape=7),
    inp("end_image", "IMAGE", en, shape=7),
]
flf_outputs = lambda p, n, lat: [
    out("positive", "CONDITIONING", p, 0),
    out("negative", "CONDITIONING", n, 1),
    out("latent", "LATENT", lat, 2),
]

nodes += [
    node(20, "WanFirstLastFrameToVideo", [1140, -80], [320, 220], flf_inputs(a_pos, a_neg, a_vae, a_cvs, a_cve, a_st, a_en), flf_outputs([a_ph, a_pl], [a_nh, a_nl], [a_lh]), flf_w, title="Clip A: 1 -> 2", order=24),
    node(21, "KSamplerAdvanced", [1500, -200], [300, 320], [inp("model", "MODEL", a_mh), inp("positive", "CONDITIONING", a_ph), inp("negative", "CONDITIONING", a_nh), inp("latent_image", "LATENT", a_lh)], [out("LATENT", "LATENT", [a_llat], 0)], ks_high, title="High A", order=25),
    node(22, "KSamplerAdvanced", [1500, 160], [300, 320], [inp("model", "MODEL", a_ml), inp("positive", "CONDITIONING", a_pl), inp("negative", "CONDITIONING", a_nl), inp("latent_image", "LATENT", a_llat)], [out("LATENT", "LATENT", [a_dec_s], 0)], ks_low, title="Low A", order=26),
    node(23, "VAEDecode", [1860, -80], [220, 50], [inp("samples", "LATENT", a_dec_s), inp("vae", "VAE", a_dec_v)], [out("IMAGE", "IMAGE", [join_ab1], 0)], [], title="Frames A", order=27),
    node(30, "WanFirstLastFrameToVideo", [1140, 420], [320, 220], flf_inputs(b_pos, b_neg, b_vae, b_cvs, b_cve, b_st, b_en), flf_outputs([b_ph, b_pl], [b_nh, b_nl], [b_lh]), flf_w, title="Clip B: 2 -> 3", order=28),
    node(31, "KSamplerAdvanced", [1500, 300], [300, 320], [inp("model", "MODEL", b_mh), inp("positive", "CONDITIONING", b_ph), inp("negative", "CONDITIONING", b_nh), inp("latent_image", "LATENT", b_lh)], [out("LATENT", "LATENT", [b_llat], 0)], ks_high, title="High B", order=29),
    node(32, "KSamplerAdvanced", [1500, 660], [300, 320], [inp("model", "MODEL", b_ml), inp("positive", "CONDITIONING", b_pl), inp("negative", "CONDITIONING", b_nl), inp("latent_image", "LATENT", b_llat)], [out("LATENT", "LATENT", [b_dec_s], 0)], ks_low, title="Low B", order=30),
    node(33, "VAEDecode", [1860, 420], [220, 50], [inp("samples", "LATENT", b_dec_s), inp("vae", "VAE", b_dec_v)], [out("IMAGE", "IMAGE", [skip_b], 0)], [], title="Frames B", order=31),
    node(40, "WanFirstLastFrameToVideo", [1140, 920], [320, 220], flf_inputs(c_pos, c_neg, c_vae, c_cvs, c_cve, c_st, c_en), flf_outputs([c_ph, c_pl], [c_nh, c_nl], [c_lat]), flf_w, title="Clip C: 3 -> 4", order=32),
    node(41, "KSamplerAdvanced", [1500, 800], [300, 320], [inp("model", "MODEL", c_mh), inp("positive", "CONDITIONING", c_ph), inp("negative", "CONDITIONING", c_nh), inp("latent_image", "LATENT", c_lat)], [out("LATENT", "LATENT", [c_llat], 0)], ks_high, title="High C", order=33),
    node(42, "KSamplerAdvanced", [1500, 1160], [300, 320], [inp("model", "MODEL", c_ml), inp("positive", "CONDITIONING", c_pl), inp("negative", "CONDITIONING", c_nl), inp("latent_image", "LATENT", c_llat)], [out("LATENT", "LATENT", [c_dec_s], 0)], ks_low, title="Low C", order=34),
    node(43, "VAEDecode", [1860, 920], [220, 50], [inp("samples", "LATENT", c_dec_s), inp("vae", "VAE", c_dec_v)], [out("IMAGE", "IMAGE", [skip_c], 0)], [], title="Frames C", order=35),
    node(50, "ImageFromBatch", [1860, 500], [250, 90], [inp("image", "IMAGE", skip_b)], [out("IMAGE", "IMAGE", [join_ab2], 0)], [1, 80], title="Skip first of B", order=36),
    node(51, "ImageFromBatch", [1860, 1000], [250, 90], [inp("image", "IMAGE", skip_c)], [out("IMAGE", "IMAGE", [join_abc2], 0)], [1, 80], title="Skip first of C", order=37),
    node(52, "ImageBatch", [2160, 200], [240, 50], [inp("image1", "IMAGE", join_ab1), inp("image2", "IMAGE", join_ab2)], [out("IMAGE", "IMAGE", [join_abc1], 0)], [], title="Join A+B", order=38),
    node(53, "ImageBatch", [2160, 500], [240, 50], [inp("image1", "IMAGE", join_abc1), inp("image2", "IMAGE", join_abc2)], [out("IMAGE", "IMAGE", [to_vid], 0)], [], title="Join +C", order=39),
    node(54, "CreateVideo", [2440, 200], [220, 80], [inp("images", "IMAGE", to_vid), inp("audio", "AUDIO", None, shape=7)], [out("VIDEO", "VIDEO", [to_save], 0)], [16], order=40),
    node(55, "SaveVideo", [2440, 320], [270, 120], [inp("video", "VIDEO", to_save)], [], ["video/storyboard", "auto", "auto"], order=41),
]

# Patch MODEL output links on nodes 6 and 7 after c_ml fix
for n in nodes:
    if n["id"] == 6:
        n["outputs"][0]["links"] = [a_mh, b_mh, c_mh]
    if n["id"] == 7:
        n["outputs"][0]["links"] = [a_ml, b_ml, c_ml]

wf = {
    "id": "multi-image-video",
    "revision": 0,
    "last_node_id": 74,
    "last_link_id": link_id,
    "nodes": nodes,
    "links": links,
    "groups": [
        {"id": 1, "title": "1. Photos in story order", "bounding": [-560, -250, 430, 1760], "color": "#3f789e", "font_size": 24, "flags": {}},
        {"id": 2, "title": "2. Instructions", "bounding": [430, 280, 470, 430], "color": "#3f789e", "font_size": 24, "flags": {}},
        {"id": 3, "title": "3. Models (leave unless a dropdown is red)", "bounding": [20, -120, 1080, 580], "color": "#3f789e", "font_size": 24, "flags": {}},
        {"id": 4, "title": "4. Three 5s clips then stitch", "bounding": [1110, -250, 1640, 1760], "color": "#3f789e", "font_size": 24, "flags": {}},
    ],
    "config": {},
    "extra": {
        "ds": {"scale": 0.45, "offset": [700, 700]},
        "frontendVersion": "1.47.10",
    },
    "version": 0.4,
}

OUT.write_text(json.dumps(wf, indent=2), encoding="utf-8")
print("wrote", OUT, "nodes", len(nodes), "links", len(links), "last_link", link_id)
ids = {n["id"] for n in nodes}
by_id = {n["id"]: n for n in nodes}
link_map = {item[0]: item for item in links}
for lid, o, os, t, ts, typ in links:
    if o not in ids or t not in ids:
        raise SystemExit(f"BAD LINK {lid} {o}->{t}")
for n in nodes:
    for i in n.get("inputs", []):
        lid = i.get("link")
        if not lid:
            continue
        item = link_map.get(lid)
        if not item:
            raise SystemExit(f"missing link {lid} on node {n['id']} {n['type']}")
        _, o, os, t, ts, typ = item
        if t != n["id"]:
            raise SystemExit(f"node {n['id']} {n['type']} input {i['name']} link {lid} targets {t}")
        if typ != i["type"]:
            raise SystemExit(f"node {n['id']} {n['type']} input {i['name']} wants {i['type']} got {typ}")
print("link check ok", "node6 in", by_id[6]["inputs"], "from", link_map[by_id[6]["inputs"][0]["link"]])
