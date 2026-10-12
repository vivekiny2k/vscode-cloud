#!/usr/bin/env bash
# Run by the official PyTorch /start.sh as /pre_start.sh.
# Also used as the local-compose startup path.
set -uo pipefail

# Never let Ollama listen on a public address, even if env is overridden.
OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
case "$OLLAMA_HOST" in
  0.0.0.0*|::|::*|[::]*) OLLAMA_HOST="127.0.0.1:11434" ;;
esac
OLLAMA_MODELS="${OLLAMA_MODELS:-/workspace/ollama}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5-coder:14b}"
HF_HOME="${HF_HOME:-/workspace/.cache/huggingface}"
CODE_SERVER_EXTENSIONS="${CODE_SERVER_EXTENSIONS:-/opt/code-server/extensions}"
LOG_DIR="${LOG_DIR:-/workspace/logs}"

export OLLAMA_HOST OLLAMA_MODELS OLLAMA_MODEL HF_HOME

lock_down_inbound() {
  command -v iptables >/dev/null 2>&1 || return 0
  iptables -C INPUT -p tcp --dport 8080 -j ACCEPT 2>/dev/null && return 0
  iptables -I INPUT 1 -i lo -j ACCEPT
  iptables -I INPUT 2 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  iptables -I INPUT 3 -p tcp --dport 8080 -j ACCEPT
  # Published interface is code-server only. SSH, Jupyter, Ollama, ttyd stay off the wire.
  for port in 22 8888 11434 19123; do
    iptables -A INPUT -p tcp --dport "$port" -j DROP
  done
}

mkdir -p \
  /workspace/projects \
  "$OLLAMA_MODELS" \
  /workspace/.code-server \
  /workspace/.continue \
  "$HF_HOME" \
  "$LOG_DIR"

if [ ! -f /workspace/.continue/config.yaml ]; then
  sed "s/qwen2.5-coder:14b/${OLLAMA_MODEL}/g" /opt/vscode-cloud/continue.yaml \
    > /workspace/.continue/config.yaml
fi
if [ ! -f /workspace/.continue/config.json ]; then
  sed "s/qwen2.5-coder:14b/${OLLAMA_MODEL}/g" /opt/vscode-cloud/continue.json \
    > /workspace/.continue/config.json
fi
ln -sfn /workspace/.continue /root/.continue

if [ -z "${PASSWORD:-}" ] && [ -z "${HASHED_PASSWORD:-}" ]; then
  PASSWORD="$(openssl rand -base64 24 | tr -dc 'A-Za-z0-9' | head -c 20)"
  export PASSWORD
  printf '%s\n' "$PASSWORD" > /workspace/code-server.password
  chmod 600 /workspace/code-server.password
  echo "PASSWORD was unset; wrote a generated password to /workspace/code-server.password" \
    >> "$LOG_DIR/code-server.log"
fi
export PASSWORD
export HASHED_PASSWORD="${HASHED_PASSWORD:-}"

if ! pgrep -x ollama >/dev/null 2>&1; then
  setsid bash -c 'exec ollama serve' >>"$LOG_DIR/ollama.log" 2>&1 </dev/null &
fi

if ! pgrep -f '[c]ode-server --bind-addr' >/dev/null 2>&1; then
  setsid bash -c \
    "exec code-server --bind-addr 0.0.0.0:8080 --auth password \
      --user-data-dir /workspace/.code-server \
      --extensions-dir ${CODE_SERVER_EXTENSIONS} \
      --config /opt/vscode-cloud/code-server.yaml" \
    >>"$LOG_DIR/code-server.log" 2>&1 </dev/null &
fi

setsid bash -c '
  for i in $(seq 1 90); do
    curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null && break
    sleep 2
  done
  if ! ollama list 2>/dev/null | awk "NR>1 {print \$1}" | grep -qx "'"${OLLAMA_MODEL}"'"; then
    ollama pull "'"${OLLAMA_MODEL}"'"
  fi
  echo "LISTEN $(ss -lnt 2>/dev/null || netstat -lnt 2>/dev/null)"
  echo "SELFTEST_BEGIN $(date -u +%FT%TZ)"
  curl -sf --max-time 180 http://127.0.0.1:11434/api/generate \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"'"${OLLAMA_MODEL}"'\",\"prompt\":\"Reply with exactly SELFTEST_OK and nothing else.\",\"stream\":false,\"options\":{\"num_predict\":16}}" \
    && echo && echo "SELFTEST_DONE $(date -u +%FT%TZ)"
' >>"$LOG_DIR/selftest.log" 2>&1 </dev/null &

lock_down_inbound

exit 0
