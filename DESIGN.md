# VS Code Cloud — pod design

A browser VS Code workbench, a curated extension pack, and a local coder LLM
run together inside one Runpod GPU pod. The laptop only needs a browser.

This is the implementation spec. The visual companion is the canvas
`vscode-cloud-pod-design.canvas.tsx`.

## Goal

Encapsulate three things that usually live in different places:

| Piece | Typical setup | This project |
| --- | --- | --- |
| IDE | VS Code / Cursor on the laptop | `code-server` in the pod |
| Plugins | Local marketplace | Baked Open VSX pack + Continue |
| LLM | Cloud API or a separate GPU box | Ollama on loopback, GPU in the same pod |

Success: open `https://<pod-id>-8080.proxy.runpod.net`, log in, chat with the
on-pod model, edit files under `/workspace/projects`, stop the pod, start it
again, and the files + model weights are still there.

## Workload shape

This is a **pod**, not serverless.

- The workbench is a long-lived HTTP + websocket session.
- The model should stay loaded on the GPU.
- `/workspace` is a network volume so projects and weights survive stop/terminate.

Serverless is the wrong shape: cold starts, job timeouts, and no sticky IDE.

Remote-SSH (Runpod golden path 06) is also the wrong shape for this repo. That
path keeps the editor and plugins on the laptop. Encapsulation requires the
editor inside the container.

## Catalog constraint

Checked live against Runpod’s public templates:

- **Official:** PyTorch 2.1–2.8, ComfyUI, Ubuntu, network file browser. No VS Code.
- **Verified:** vLLM Latest, KoboldCpp, AI Toolkit. Inference UIs, not an IDE.

v1 is therefore a **custom image** built `FROM` the official PyTorch 2.8 base
so CUDA/torch match the hosts and the base layers are pre-cached:

```
runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404
```

Template id if launching the base as-is: `runpod-torch-v280`. We do not launch
it as-is; we layer code-server + Ollama on top.

## Architecture

```
Browser
  → Runpod HTTPS proxy  (public, no platform auth)
    → code-server :8080  (PASSWORD required)
         → Continue + other extensions
              → http://127.0.0.1:11434   Ollama (not published)
                   → GPU coder model
         → /workspace                    network volume
```

Three processes, one public URL.

| Process | Bind | Published? |
| --- | --- | --- |
| code-server | `0.0.0.0:8080` | `8080/http` |
| sshd | (base image) | `22/tcp` |
| Ollama | `127.0.0.1:11434` | **no** |

Do not expose Jupyter `:8888` even though the PyTorch base can start it.

## Image contract

Official `runpod/pytorch` images use `CMD ["/start.sh"]`. That script:

1. Injects `$PUBLIC_KEY` into `authorized_keys`
2. Starts `sshd` and the web terminal
3. Runs `/pre_start.sh` then `/post_start.sh` if present

**Do not replace `CMD`.** Add `/post_start.sh` that:

1. `mkdir -p` volume paths
2. `export OLLAMA_HOST=127.0.0.1:11434`
3. `export OLLAMA_MODELS=/workspace/ollama`
4. Starts Ollama detached (`setsid`, stdin from `/dev/null`)
5. Starts code-server detached on `:8080` with `--user-data-dir /workspace/.code-server`
6. If the default model is missing, `ollama pull` in the background — do not
   block boot on a multi-GB download

Ready signal is **not** pod status `RUNNING`. Poll the proxy URL until
code-server returns 200. Expect 502s for 30–60s.

## Bake vs mount

Network volumes are FUSE. Thousands of small files are slow. Model blobs are
few large files and belong on the volume.

**Bake (image, local overlay):**

- code-server binary (pin a release)
- Ollama binary
- Open VSX extensions (Continue, Python, Jupyter, Git, ESLint, EditorConfig)
- Continue `config.json` template pointing at localhost Ollama
- `/post_start.sh`

**Mount (`/workspace` network volume):**

| Path | Contents |
| --- | --- |
| `/workspace/projects` | User repos |
| `/workspace/ollama` | Ollama blobs (`OLLAMA_MODELS`) |
| `/workspace/.code-server` | Settings, UI state, unsaved editors |
| `/workspace/.cache/huggingface` | Optional HF cache (`HF_HOME`) |

Stop/restart **wipes `/root` and the rest of the container disk**. Anything
not under `/workspace` or baked into the image is gone. The volume is pinned
to one data center; the pod must be created in that same DC.

Suggested volume size for v1: **50 GB**.

## Extensions

Marketplace is **Open VSX**, not Microsoft’s. That rules out GitHub Copilot
and often Pylance.

v1 pack:

- `Continue.continue` — chat + autocomplete against Ollama
- Python + Jupyter (Open VSX builds)
- Git, ESLint, EditorConfig, Prettier

Continue config (baked, overridable on the volume):

```json
{
  "models": [
    {
      "title": "Qwen2.5-Coder 14B",
      "provider": "ollama",
      "model": "qwen2.5-coder:14b"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen2.5-Coder 14B",
    "provider": "ollama",
    "model": "qwen2.5-coder:14b"
  }
}
```

Do not keep a 14B and a 7B hot at the same time on a 24 GB card.

## GPU and models

Live Secure Cloud pod catalog (this design session):

| GPU | VRAM | Secure $/hr | Availability | Use |
| --- | --- | --- | --- | --- |
| RTX 4090 | 24 GB | $0.74 | LOW · EU-RO-1, EUR-IS-2 | **v1 default** — fast Ada, 14B Q4 |
| L4 | 24 GB | $0.49 | LOW · EU-RO-1, US-MO-2 | Cheaper 24 GB fallback |
| A40 | 48 GB | $0.49 | LOW · EU-SE-1 | 32B Q4 / more context |
| RTX A6000 | 48 GB | $0.53 | LOW · EU-SE-1 | Same class as A40 |
| A100 SXM 80GB | 80 GB | $1.59 | LOW · several US/EU | 32B fp16 or 70B Q4 |

Community 4090 is $0.34/hr if cost matters more than stable IPs.

Default model: **`qwen2.5-coder:14b`** (Q4 via Ollama). Fits a 24 GB card with
room for ~8–16k context. Override with `OLLAMA_MODEL`.

On 24 GB, budget roughly: 9 GB weights + 6 GB KV + 4 GB Ollama/CUDA + 2 GB IDE.

Confirm stock with `list-gpu-types` (`include=AVAILABILITY`, `product=POD`)
before creating a pod. Do not create into a class with `availability: NONE`.

## Ports, env, auth

Create-time ports (cannot be added later without reset):

```
8080/http,22/tcp
```

Required env:

| Variable | Value |
| --- | --- |
| `PASSWORD` | code-server login (required; proxy has no auth) |
| `OLLAMA_HOST` | `127.0.0.1:11434` |
| `OLLAMA_MODELS` | `/workspace/ollama` |
| `OLLAMA_MODEL` | `qwen2.5-coder:14b` |
| `HF_HOME` | `/workspace/.cache/huggingface` |

The proxy URL is **public and unauthenticated at the platform layer**. Handing
someone the URL without a `PASSWORD` publishes the workbench.

Ollama must not be published. If `11434/http` is added, the model is a public
GPU API.

## First pod shape

- GPU: RTX 4090 (L4 if 4090 is out)
- Cloud: Secure unless cost is the constraint
- Network volume: 50 GB, same DC as the GPU, mount `/workspace`
- Container disk: 30 GB
- Ports: `8080/http,22/tcp`
- Cost guard: `--stop-after` for a kept box; `--terminate-after` for tests

SSH keys must be registered on the account **before** the pod boots.

## Implementation order

1. Dockerfile `FROM` the pinned PyTorch 2.8 tag; inherit `CMD ["/start.sh"]`.
2. Install pinned code-server; user data on `/workspace/.code-server`.
3. Bake the Open VSX pack into the image (not onto the volume).
4. Install Ollama; models directory on the volume; loopback bind.
5. `/post_start.sh` starts Ollama, then code-server; model pull is background.
6. Ship Continue config for localhost Ollama.
7. Publish an account template with the ports and required `PASSWORD`.
8. Verify from outside: proxy 200, login, chat, write a marker under
   `/workspace/projects`, stop → start, marker still there.

## Out of scope for v1

- Cursor desktop in the pod (not a server)
- GitHub Copilot / Pylance
- Public Ollama or vLLM URL
- Multi-user / team auth beyond a shared password
- Serverless scale-to-zero of this stack
- Baking model weights into the image (too large, too sticky)

vLLM can later replace Ollama behind the same Continue OpenAI endpoint if
token throughput becomes the bottleneck. The IDE contract does not change.
