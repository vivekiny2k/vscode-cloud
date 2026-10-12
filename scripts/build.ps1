param(
  [ValidateSet("local", "production")]
  [string]$Target = "local",
  [string]$Tag = "",
  [string]$CodeServerVersion = "4.137.0",
  [string]$OllamaVersion = "0.34.2"
)

$ErrorActionPreference = "Stop"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Error "Docker is not installed. Install Docker Desktop, then re-run this script."
}

if (-not $Tag) {
  $Tag = if ($Target -eq "local") { "vscode-cloud:local-v0.1.0" } else { "vscode-cloud:v0.1.0" }
}

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

docker build --platform linux/amd64 --target $Target `
  --build-arg CODE_SERVER_VERSION=$CodeServerVersion `
  --build-arg OLLAMA_VERSION=$OllamaVersion `
  -t $Tag `
  $root

Write-Host "Built $Tag"
if ($Target -eq "local") {
  Write-Host "Run: docker compose up"
} else {
  Write-Host "Tag for a registry you control, then: docker push <ns>/vscode-cloud:v0.1.0"
}
