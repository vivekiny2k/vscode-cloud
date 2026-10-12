#!/usr/bin/env bash
set -euo pipefail
M=/workspace/runpod-slim/ComfyUI/models
B=https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files
LOG=/workspace/wan-i2v-download.log
mkdir -p "$M/diffusion_models" "$M/text_encoders" "$M/vae" "$M/clip_vision"
echo "START $(date -u +%FT%TZ)" | tee "$LOG"
dl() { curl -L --retry 5 --retry-delay 5 -C - -o "$1" "$2"; }
dl "$M/vae/wan_2.1_vae.safetensors" "$B/vae/wan_2.1_vae.safetensors"
echo "VAE_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"
dl "$M/clip_vision/clip_vision_h.safetensors" "$B/clip_vision/clip_vision_h.safetensors"
echo "CLIP_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"
dl "$M/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" "$B/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
echo "UMT5_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"
dl "$M/diffusion_models/wan2.1_i2v_480p_14B_fp8_scaled.safetensors" "$B/diffusion_models/wan2.1_i2v_480p_14B_fp8_scaled.safetensors"
echo "I2V_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"
ls -lh "$M/vae" "$M/clip_vision" "$M/text_encoders" "$M/diffusion_models" | tee -a "$LOG"
