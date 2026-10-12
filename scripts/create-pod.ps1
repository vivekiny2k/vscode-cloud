# Creates a GPU pod from a pushed image. Do not run this just to save cost —
# it bills by the hour. Fill IMAGE first (never use :latest).

param(
  [Parameter(Mandatory = $true)]
  [string]$Image,
  [string]$Name = "vscode-cloud",
  [string]$GpuId = "NVIDIA RTX PRO 4500 Blackwell",
  [string]$DataCenter = "EU-RO-1",
  [string]$VolumeId = "ffvlzhdyk4",
  [string]$Password = ""
)

$ErrorActionPreference = "Stop"
if (-not (Get-Command runpodctl -ErrorAction SilentlyContinue)) {
  $env:Path = "$env:LOCALAPPDATA\runpodctl;$env:Path"
}

if (-not $Password) {
  $Password = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 20 | ForEach-Object { [char]$_ })
}

$envJson = (@{
  PASSWORD = $Password
  OLLAMA_HOST = "127.0.0.1:11434"
  OLLAMA_MODELS = "/workspace/ollama"
  OLLAMA_MODEL = "qwen2.5-coder:14b"
  HF_HOME = "/workspace/.cache/huggingface"
} | ConvertTo-Json -Compress)

Write-Host "This will bill the GPU hourly. Image: $Image  GPU: $GpuId"
runpodctl pod create `
  --name $Name `
  --image $Image `
  --gpu-id $GpuId `
  --cloud-type SECURE `
  --data-center-ids $DataCenter `
  --network-volume-id $VolumeId `
  --volume-mount-path /workspace `
  --container-disk-in-gb 30 `
  --ports "8080/http" `
  --env "$envJson" `
  --wait

Write-Host "code-server password: $Password"
Write-Host "URL form: https://<pod-id>-8080.proxy.runpod.net (public; password is the only gate)"
