# Upload auth files to a RUNNING ComfyUI pod. Does not create or start a pod.
# Usage (when you are ready):
#   .\scripts\upload-comfyui-auth.ps1 -HostName 213.173.102.21 -Port 10252

param(
    [Parameter(Mandatory = $true)][string]$HostName,
    [Parameter(Mandatory = $true)][int]$Port,
    [string]$User = "root",
    [string]$Key = "$HOME\.runpod\ssh\runpodctl-ssh-key"
)

$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "..\comfyui-auth"
$opts = @("-i", $Key, "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL")

ssh @opts -p $Port "${User}@${HostName}" "mkdir -p /tmp/comfyui-auth"
scp @opts -P $Port `
    (Join-Path $src "__init__.py") `
    (Join-Path $src "login.html") `
    (Join-Path $src "credentials.json") `
    (Join-Path $src "install.sh") `
    "${User}@${HostName}:/tmp/comfyui-auth/"
ssh @opts -p $Port "${User}@${HostName}" "sed -i 's/\r$//' /tmp/comfyui-auth/install.sh /tmp/comfyui-auth/__init__.py && bash /tmp/comfyui-auth/install.sh"
