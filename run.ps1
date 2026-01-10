# ============================================
# Universal Chatbot - Quick Run Script (Windows)
# ============================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Starting Universal Chatbot..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check virtual environment
if (-Not (Test-Path "venv")) {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Activate venv
Write-Host "→ Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if Ollama is running
Write-Host "→ Checking Ollama service..." -ForegroundColor Yellow
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue

if ($ollamaProcess) {
    Write-Host "✓ Ollama is already running" -ForegroundColor Green
} else {
    Write-Host "→ Starting Ollama service in background..." -ForegroundColor Yellow
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 4
    Write-Host "✓ Ollama started" -ForegroundColor Green
}

Write-Host ""
Write-Host "✓ Starting Streamlit chat interface..." -ForegroundColor Green
Write-Host "  URL → http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Launch the app
streamlit run frontend.py

