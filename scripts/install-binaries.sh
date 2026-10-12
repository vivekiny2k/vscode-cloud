#!/usr/bin/env bash
# Install pinned code-server + Ollama into a Debian/Ubuntu image.
set -euo pipefail

CODE_SERVER_VERSION="${CODE_SERVER_VERSION:-4.137.0}"
OLLAMA_VERSION="${OLLAMA_VERSION:-0.34.2}"

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates curl openssl procps zstd
rm -rf /var/lib/apt/lists/*

curl -fsSL -o /tmp/code-server.deb \
  "https://github.com/coder/code-server/releases/download/v${CODE_SERVER_VERSION}/code-server_${CODE_SERVER_VERSION}_amd64.deb"
dpkg -i /tmp/code-server.deb
rm -f /tmp/code-server.deb

ollama_url="https://github.com/ollama/ollama/releases/download/v${OLLAMA_VERSION}/ollama-linux-amd64.tar.zst"
if curl -fsSL -o /tmp/ollama.tar.zst "$ollama_url"; then
  zstd -d /tmp/ollama.tar.zst -o /tmp/ollama.tar
  tar -C /usr -xf /tmp/ollama.tar
  rm -f /tmp/ollama.tar /tmp/ollama.tar.zst
else
  curl -fsSL -o /tmp/ollama.tgz \
    "https://github.com/ollama/ollama/releases/download/v${OLLAMA_VERSION}/ollama-linux-amd64.tgz"
  tar -C /usr -xzf /tmp/ollama.tgz
  rm -f /tmp/ollama.tgz
fi

if ! command -v ollama >/dev/null 2>&1; then
  found="$(find /usr /opt /bin -type f -name ollama 2>/dev/null | head -n 1)"
  if [ -n "$found" ]; then
    ln -sf "$found" /usr/bin/ollama
  fi
fi

command -v code-server
command -v ollama
code-server --version
ollama --version || true
