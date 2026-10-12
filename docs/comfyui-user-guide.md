# ComfyUI user guide (this pod)

This is how to use the **node graph** on the ComfyUI site — the canvas of boxes and wires — without needing to understand every node. Nothing here starts a GPU. Open the URLs only after the `comfyui-i2v` pod is already running.

| When the pod is running | URL | Login |
| --- | --- | --- |
| Simple page (photo + prompt only) | `https://<pod-id>-8188.proxy.runpod.net/i2v` | `admin` / see `comfyui-auth/credentials.json` |
| Full ComfyUI graph | `https://<pod-id>-8188.proxy.runpod.net/` | same |
| FileBrowser (files on disk) | `https://<pod-id>-8080.proxy.runpod.net/` | same |

Auth is built in this repo (`comfyui-auth/`). It is **not on the pod yet**. After you start the pod, upload that folder and run `install.sh` on it. ComfyUI must restart once so `/login` loads. FileBrowser picks up the new password immediately. Jupyter still uses `JUPYTER_PASSWORD` until you set that env to the same password on the next start.

Last pod id used for this setup: `iql7hrzn0v6xw0`.

Use `/i2v` when you only want a picture and a prompt. Use the graph when you want a downloaded workflow, different size/length, first-and-last-frame, extra LoRAs, or anything the simple page does not expose.

---

## 1. What the site actually is

ComfyUI is not a single form. It is a **pipeline drawn as boxes**.

- Each **box** is a step (load a model, encode a prompt, sample, save a video).
- Each **wire** is data moving to the next step (an image, a prompt embedding, a latent, a video).
- **Run** (or `Ctrl+Enter`) executes the whole graph. ComfyUI only recomputes boxes whose inputs changed.

You do not “fill in” empty boxes by typing into the void. You either pick a file from a dropdown on that box, or you change a text/number widget that is already on it.

A **red outline** or a sidebar list of missing files means a dropdown is empty or the filename in the workflow is not on disk. The graph is still valid — it just cannot run until those files are chosen.

---

## 2. The chrome (where to click)

Top bar:

- **Workflow** — Open, Save, Export, Browse templates.
- **Run** — queues the current graph (`Ctrl+Enter`). The number on the button is how many jobs are waiting.
- Tab name — the workflow you have open. You can have more than one tab.

Left sidebar (icons):

- **Queue** — running and finished jobs.
- **Node library** — search “Load Image”, “CLIP Text Encode”, etc., then drag onto the canvas.
- **Model library** — files already under `ComfyUI/models/`. Press `R` after you add files so dropdowns refresh.
- **Workflows** — graphs you saved on this pod.
- **Templates** — official ready-made graphs (this is the easiest way to get Wan 2.2 I2V).
- **Assets** — recent outputs.

Canvas:

- Scroll to zoom. Hold **Space** and drag to pan. `.` fits the selected nodes.
- Double-click empty canvas → search and add a node.
- Click a box once → its sliders and dropdowns are on the box itself (and often in the right panel).
- Drag from a **dot on the right** of a box to a **dot on the left** of another box to wire them. Colors must match (IMAGE to IMAGE, MODEL to MODEL).

Manager / Civicomfy / RunpodDirect sit in the top menu on this image. They download models into the right folder. You do not need them if the files are already on the volume.

---

## 3. How to use a complicated workflow (the short method)

A “complicated flow” is just a saved graph. Treat it as a machine with **three knobs**. Ignore the rest until something breaks.

### Load it

Any one of these:

1. Left sidebar → **Templates** → search `Wan2.2` or `I2V` → open **Wan2.2 14B I2V** (or the Lightning variant you used).
2. **Workflow → Open** (`Ctrl+O`) and pick a `.json`.
3. Drag a `.json` **or** a PNG/WebP that was exported from ComfyUI onto the canvas. Generated files often embed the graph.

If the canvas shows a few large boxes and one fat group titled something like **Image to Video (Wan2.2)**, that fat box is a **subgraph**. The official Wan 2.2 I2V template works this way. You use the subgraph like a form:

- drop / choose the start **image**
- type the **prompt**
- optionally change width, height, seed
- click **Run**

Do not open the subgraph unless you need to change models or sampler internals.

To open it: double-click the subgraph (or use the expand control on it). To leave: use the breadcrumb / back control at the top so you return to the outer graph. Do not delete wires on the way out.

### Make it runnable

1. Click each red or empty loader. Open its dropdown. Pick the file that is already on the pod (see [§5](#5-this-pods-wan-22-image-to-video-graph)).
2. If the sidebar still lists downloads, either wait them out or ignore them once the dropdowns show real filenames.
3. Press `R` if a file is on disk but the dropdown is still empty.
4. On **Load Image**, click the image area / “choose file” and upload your photo. That is the only image input that matters.
5. Find **CLIP Text Encode** titled positive (or the prompt field on the subgraph). Replace the example sentence with what should happen in the video. Write motion, not a still caption: “she turns toward the camera and the cloth moves” beats “a woman in a room”.
6. Leave the negative prompt alone unless you know why you are changing it. The stock Chinese block on Wan graphs is the default quality filter.
7. **Run** / `Ctrl+Enter`. First run after boot loads ~14 GB models into VRAM and is slow (about 1–2 minutes for Lightning I2V). Later runs on the same models are faster.

### Where the result appears

- On the **Save Video** (or Preview) node on the right of the graph — click it, play / right-click save.
- Left sidebar → **Assets** or **Queue** → the finished job.
- FileBrowser: `runpod-slim/ComfyUI/output/` (this setup writes `output/video/i2v_#####_.mp4`).
- Direct play URL while the pod is up:

  `https://<pod-id>-8188.proxy.runpod.net/view?filename=i2v_00001_.mp4&subfolder=video&type=output`

---

## 4. What you should and should not touch

**Safe to change** on an I2V graph:

| Control | Typical node | Effect |
| --- | --- | --- |
| Start picture | Load Image | First frame |
| Positive prompt | CLIP Text Encode (the non-red one) | What happens |
| Seed | KSampler (Advanced) or subgraph seed | Different motion, same setup |
| Width / height | WanImageToVideo | Must stay multiples of 16. 640×640 is the official Lightning default. Larger = more VRAM and time |
| Length | WanImageToVideo `length` | Frame count. 81 frames at 16 fps ≈ 5 seconds. Step is 4 (81, 77, 73, …) |

**Leave alone** until you have a reason:

- The two **Load Diffusion Model** boxes (high-noise and low-noise). Wan 2.2 I2V is a pair. Swapping one for a T2V or 2.1 file will fail or look wrong.
- The two **Load LoRA** boxes (HIGH / high_noise and LOW / low_noise). Lightning is 4 steps *because* these LoRAs are on. Remove them and you need ~20 steps and different CFG.
- **Load CLIP** type must stay `wan`. **Load VAE** must stay `wan_2.1_vae.safetensors` for the 14B I2V line.
- Sampler split: high-noise runs steps **0→2** with leftover noise **enabled**; low-noise runs **2→4** with add-noise **disabled**. That is the official 4-step Lightning recipe (CFG 1, euler, simple).
- Do not delete wires. A dangling input is why a “I only changed the prompt” run suddenly errors.

Mute (`Ctrl+M`) turns a node off as if it were deleted. Bypass (`Ctrl+B`) skips it but tries to pass data through. Use Bypass on an optional LoRA you want to A/B. Do not Bypass a VAE or sampler.

---

## 5. This pod’s Wan 2.2 image-to-video graph

Left to right, that is all the complicated flow is doing:

```
photo ──► resize ──► CLIP Vision encode ──┐
prompt ──► CLIP (umt5, type wan) ─────────┤
negative ─► CLIP (same) ──────────────────┤
VAE ──────────────────────────────────────► WanImageToVideo ──► latent
                                              │
high UNET + HIGH Lightning LoRA + shift 5 ──► KSampler 0→2 ──┐
                                                              ├──► KSampler 2→4 ──► VAE decode ──► video
low UNET  + LOW  Lightning LoRA + shift 5 ────────────────────┘
```

Files already staged on the volume (dropdown names):

| Role | Filename | Folder |
| --- | --- | --- |
| High-noise video model | `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` | `models/diffusion_models/` |
| Low-noise video model | `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` | `models/diffusion_models/` |
| Lightning LoRA (high) | `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` or `Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors` | `models/loras/` |
| Lightning LoRA (low) | `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` or `Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors` | `models/loras/` |
| Text encoder | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `models/text_encoders/` |
| VAE | `wan_2.1_vae.safetensors` | `models/vae/` |
| CLIP Vision | `clip_vision_h.safetensors` | `models/clip_vision/` |

If a loader still shows the old red “download” name, open the dropdown and pick one of the rows above. Pair HIGH with high-noise and LOW with low-noise. Do not mix T2V files into this graph.

On-disk layout (FileBrowser, root is `/workspace`):

```
runpod-slim/ComfyUI/
├── models/
│   ├── diffusion_models/
│   ├── loras/
│   ├── text_encoders/
│   ├── vae/
│   └── clip_vision/
├── input/          ← uploads from Load Image
└── output/video/   ← mp4 from the simple UI and Save Video
```

---

## 6. Loading someone else’s complicated flow

Community graphs (Civitai, OpenArt, Reddit) arrive as JSON or as a PNG with metadata.

1. Drag the file onto the canvas.
2. Read the toast / red nodes. Two different failures look similar:
   - **Missing models** — dropdown empty. Put the file in the folder the node type uses, press `R`, pick it.
   - **Missing node type** — the box shows an unknown class (or the graph refuses to load). That workflow needs extra custom nodes. This image already has Manager, KJNodes, Civicomfy, RunpodDirect. Anything else (WanVideoWrapper, GGUF, Video Helper Suite, …) you install with **Manager → Install Custom Nodes**, then restart ComfyUI. Do not add nodes “just in case”.
3. Confirm the graph is actually I2V: there must be a **Load Image** (or start_image) feeding a Wan / I2V latent node. A T2V graph has no start image; a first-last-frame graph has two images.
4. Replace only the image and the positive prompt, then Run once before you edit samplers.

Official extra Wan templates (same site, **Templates** search):

- **Wan2.2 14B I2V** — image to video (what you have weights for).
- **Wan2.2 14B T2V** — text only; needs the T2V high/low files, not the I2V ones.
- **Wan2.2 14B FLF2V** — first and last frame; two Load Image nodes.
- **Wan2.2 5B TI2V** — different VAE (`wan2.2_vae`) and a single 5B model. Do not point it at the 14B I2V files.

---

## 7. Shortcuts worth memorizing

| Key | Action |
| --- | --- |
| `Ctrl+Enter` | Run / queue |
| `Ctrl+Alt+Enter` | Interrupt the current job |
| `Ctrl+O` / `Ctrl+S` | Open / save workflow |
| `R` | Refresh model lists after a download |
| `Ctrl+B` | Bypass selected nodes |
| `Ctrl+Z` | Undo a bad wire |
| `Q` / `N` / `M` | Queue / node library / model library |
| Space + drag | Pan |

---

## 8. When a run fails

- **Immediate error, no GPU heat** — a dropdown is still empty, a wire is missing, or width/height is not a multiple of 16. Read the red toast; it names the node.
- **OOM / CUDA out of memory** — drop width/height toward 640, or cut `length` (try 49). Do not load a second 14B graph in another tab and Run both.
- **Video is a still** — prompt describes a pose, not a motion. Say what moves. CFG for Lightning must stay at **1**. Raising CFG with these LoRAs often freezes or artifacts.
- **Wrong face / ignores the photo** — you ran a T2V template, or Load Image is not wired into WanImageToVideo `start_image`.
- **Queue sits at 0 and nothing happens** — you are on the simple `/i2v` page vs the graph, or you interrupted. Check **Queue**.

---

## 9. Simple page vs graph

| | `/i2v` | Graph |
| --- | --- | --- |
| What you do | Upload + prompt + Generate | Load a workflow, set 2–3 widgets, Run |
| What is fixed | Wan 2.2 Lightning I2V, 4 steps, ~5 s | Whatever the JSON says |
| Best for | Repeatable I2V | New templates, extra nodes, experiments |
| Result | Plays on the page; also `output/video/` | Save Video node + `output/` |

Both talk to the same ComfyUI server. A graph job and a `/i2v` job share one GPU queue.

---

## 10. Cost note

This guide does not start the pod. Storage for the 100 GB volume stays on whether the GPU is up. GPU time starts only when you start `comfyui-i2v`.
