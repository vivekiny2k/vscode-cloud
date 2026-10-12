# VS Code Cloud

Browser VS Code + Open VSX extensions + a local coder LLM, packaged as a Runpod
pod image. Spec: [DESIGN.md](DESIGN.md).

## Layout

| Path | Role |
| --- | --- |
| `Dockerfile` | `production` (Runpod PyTorch 2.8) and `local` (Debian CPU smoke) |
| `scripts/post_start.sh` | Starts Ollama (loopback) then code-server (`:8080`) after SSH |
| `config/` | Continue config, Open VSX extension list, code-server bind |
| `docker-compose.yml` | Local CPU IDE at http://127.0.0.1:8080 |

Production **does not replace** `/start.sh`. The PyTorch base keeps SSH; we only
add `/post_start.sh`.

Bake vs mount:

- **Image:** code-server 4.137.0, Ollama 0.34.2, Continue + Python/Jupyter/ESLint/Prettier/EditorConfig
- **Volume `/workspace`:** projects, Ollama blobs, editor state, Continue overrides

## Local (no GPU billing)

Docker is required. This machine did not have Docker or WSL when the repo was
written — install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
first.

```powershell
copy env.example .env
# edit PASSWORD
.\scripts\build.ps1 -Target local
docker compose up --build
```

Open http://127.0.0.1:8080 and log in with `PASSWORD` from `.env` (default
`localdev`). The local image pulls `qwen2.5-coder:1.5b` so a laptop CPU can
finish. That is a smoke test, not the 14B GPU model.

Ready signal: `GET /login` returns 200. A compose `healthy` state is that check.

## Production image (for the next pod start)

```powershell
.\scripts\build.ps1 -Target production -Tag YOUR_DOCKERHUB_USER/vscode-cloud:v0.1.0
docker push YOUR_DOCKERHUB_USER/vscode-cloud:v0.1.0
```

Always `--platform linux/amd64`. Never tag `latest`.

Existing account wiring (do not recreate unless you intend to bill):

| Resource | Id |
| --- | --- |
| Stopped pod (binaries wiped on stop) | `lmvoyjd02borj3` |
| Network volume 50 GB, EU-RO-1 | `ffvlzhdyk4` |

The stopped pod still runs the **stock** PyTorch image. After you push, start a
**new** pod from the custom image (ports cannot change in place):

```powershell
.\scripts\create-pod.ps1 -Image YOUR_DOCKERHUB_USER/vscode-cloud:v0.1.0
```

That script bills GPU time. Ports: `8080/http,22/tcp`. Ollama stays on
`127.0.0.1:11434` and is not published.

Proxy URL `https://<pod-id>-8080.proxy.runpod.net` is public. `PASSWORD` is the
only login.

## Env

| Variable | Default | Notes |
| --- | --- | --- |
| `PASSWORD` | required | code-server. Generated onto `/workspace/code-server.password` if missing |
| `OLLAMA_HOST` | `127.0.0.1:11434` | Loopback only |
| `OLLAMA_MODELS` | `/workspace/ollama` | Survives stop |
| `OLLAMA_MODEL` | `qwen2.5-coder:14b` (prod) / `1.5b` (local) | Pulled in the background after boot |
| `HF_HOME` | `/workspace/.cache/huggingface` | |

## Proven on Runpod (adhoc, not this image)

A live install on `lmvoyjd02borj3` already proved the loop: code-server 4.137.0
on `:8080`, Ollama 0.34.2 on loopback with CUDA, `qwen2.5-coder:14b` on the
volume, Continue installed. Stop wiped `/usr` copies of those binaries — that is
why this image exists.
