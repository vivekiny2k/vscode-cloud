# syntax=docker/dockerfile:1.6
# Default target is `production` (Runpod). Use `--target local` for a CPU smoke image.

ARG CODE_SERVER_VERSION=4.137.0
ARG OLLAMA_VERSION=0.34.2

FROM debian:bookworm-slim AS local
ARG CODE_SERVER_VERSION
ARG OLLAMA_VERSION
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    OLLAMA_HOST=127.0.0.1:11434 \
    OLLAMA_MODELS=/workspace/ollama \
    OLLAMA_MODEL=qwen2.5-coder:1.5b \
    HF_HOME=/workspace/.cache/huggingface \
    CODE_SERVER_EXTENSIONS=/opt/code-server/extensions \
    SERVICE_URL=https://open-vsx.org/vscode/gallery \
    ITEM_URL=https://open-vsx.org/vscode/item
COPY scripts/install-binaries.sh /tmp/install-binaries.sh
RUN sed -i 's/\r$//' /tmp/install-binaries.sh \
    && chmod +x /tmp/install-binaries.sh \
    && CODE_SERVER_VERSION=${CODE_SERVER_VERSION} OLLAMA_VERSION=${OLLAMA_VERSION} \
       bash /tmp/install-binaries.sh \
    && rm -f /tmp/install-binaries.sh
COPY config/ /opt/vscode-cloud/
COPY scripts/install-extensions.sh /tmp/install-extensions.sh
RUN sed -i 's/\r$//' /tmp/install-extensions.sh \
    && chmod +x /tmp/install-extensions.sh \
    && bash /tmp/install-extensions.sh /opt/vscode-cloud/extensions.txt \
    && rm -f /tmp/install-extensions.sh
COPY scripts/post_start.sh /post_start.sh
COPY scripts/local-entrypoint.sh /opt/vscode-cloud/local-entrypoint.sh
RUN sed -i 's/\r$//' /post_start.sh /opt/vscode-cloud/local-entrypoint.sh \
    && chmod +x /post_start.sh /opt/vscode-cloud/local-entrypoint.sh
EXPOSE 8080
CMD ["/opt/vscode-cloud/local-entrypoint.sh"]

FROM runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 AS production
ARG CODE_SERVER_VERSION
ARG OLLAMA_VERSION
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    OLLAMA_HOST=127.0.0.1:11434 \
    OLLAMA_MODELS=/workspace/ollama \
    OLLAMA_MODEL=qwen2.5-coder:14b \
    HF_HOME=/workspace/.cache/huggingface \
    CODE_SERVER_EXTENSIONS=/opt/code-server/extensions \
    SERVICE_URL=https://open-vsx.org/vscode/gallery \
    ITEM_URL=https://open-vsx.org/vscode/item
COPY scripts/install-binaries.sh /tmp/install-binaries.sh
RUN sed -i 's/\r$//' /tmp/install-binaries.sh \
    && chmod +x /tmp/install-binaries.sh \
    && CODE_SERVER_VERSION=${CODE_SERVER_VERSION} OLLAMA_VERSION=${OLLAMA_VERSION} \
       bash /tmp/install-binaries.sh \
    && rm -f /tmp/install-binaries.sh
COPY config/ /opt/vscode-cloud/
COPY scripts/install-extensions.sh /tmp/install-extensions.sh
RUN sed -i 's/\r$//' /tmp/install-extensions.sh \
    && chmod +x /tmp/install-extensions.sh \
    && bash /tmp/install-extensions.sh /opt/vscode-cloud/extensions.txt \
    && rm -f /tmp/install-extensions.sh
COPY scripts/post_start.sh /pre_start.sh
RUN sed -i 's/\r$//' /pre_start.sh && chmod +x /pre_start.sh \
    && ln -sfn /pre_start.sh /post_start.sh
# Official /start.sh only executes /pre_start.sh. Do not set CMD.
EXPOSE 8080
