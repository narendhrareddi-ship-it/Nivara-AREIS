# Start local Ollama for NIVARA (Windows). Run from repo root or launchers folder.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Starting Ollama via docker compose..."
    docker compose up -d ollama
    Write-Host "Pulling llama3.2 (first run may take several minutes)..."
    docker exec nivara-ollama ollama pull llama3.2
}
elseif (Get-Command ollama -ErrorAction SilentlyContinue) {
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 | Out-Null
    }
    catch {
        Write-Host "Starting ollama serve..."
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
    }
    ollama pull llama3.2
}
else {
    Write-Host "Install Ollama from https://ollama.com/download"
    Write-Host "Or install Docker Desktop and run: docker compose up -d ollama"
    exit 1
}

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | Out-Null
    Write-Host "Ollama is live at http://localhost:11434"
}
catch {
    Write-Host "Ollama failed to start."
    exit 1
}
