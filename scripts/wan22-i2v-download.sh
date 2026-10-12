#!/usr/bin/env bash
set -euo pipefail
M=/workspace/runpod-slim/ComfyUI/models
B=https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files
LOG=/workspace/wan22-i2v-download.log
mkdir -p "$M/diffusion_models" "$M/loras"
echo "START $(date -u +%FT%TZ)" | tee "$LOG"
dl() { curl -L --retry 5 --retry-delay 5 -C - -o "$1" "$2"; }

dl "$M/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors" \
  "$B/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"
echo "HIGH_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"

dl "$M/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors" \
  "$B/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"
echo "LOW_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"

# Official LightX2V 4-step I2V LoRAs (Comfy-Org names).
dl "$M/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors" \
  "$B/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"
echo "LORA_HIGH_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"

dl "$M/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors" \
  "$B/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"
echo "LORA_LOW_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"

# Also try the Lightning fp16 names the Manager sidebar asked for.
L=https://huggingface.co/lightx2v/Wan2.2-Lightning/resolve/main
for name in \
  "Wan2.2-Lightning_I2V-A14B-4steps-lora_HIGH_fp16.safetensors" \
  "Wan2.2-Lightning_I2V-A14B-4steps-lora_LOW_fp16.safetensors"
do
  if curl -fsI -L --max-time 20 "$L/$name" >/dev/null 2>&1; then
    dl "$M/loras/$name" "$L/$name"
    echo "LIGHTNING_$name DONE $(date -u +%FT%TZ)" | tee -a "$LOG"
  else
    echo "SKIP $name (404)" | tee -a "$LOG"
  fi
done

ls -lh "$M/diffusion_models" "$M/loras" | tee -a "$LOG"
echo "ALL_DONE $(date -u +%FT%TZ)" | tee -a "$LOG"
