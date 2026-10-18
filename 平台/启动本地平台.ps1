$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
$env:OLLAMA_MODELS=Join-Path (Split-Path $PSScriptRoot -Parent) '.runtime/models'
$env:OLLAMA_HOST='127.0.0.1:11434'
$ollamaPath=Join-Path (Split-Path $PSScriptRoot -Parent) '.runtime/ollama/ollama.exe'
try { Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null } catch {
  Start-Process -FilePath $ollamaPath -ArgumentList 'serve' -WindowStyle Hidden
}
Write-Host '打开浏览器访问 http://127.0.0.1:8787；关闭当前窗口会停止网页后端。'
node server/start.mjs
