# ============================================
# Universal Chatbot Setup Script (PowerShell)
# ============================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Universal Chatbot - Setup Script (Windows)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Upgrade pip & install dependencies
Write-Host ""
Write-Host "[4/6] Installing/upgrading Python packages..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ All Python packages installed" -ForegroundColor Green

# Check Ollama
Write-Host ""
Write-Host "[5/6] Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama found: $ollamaVersion" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Pulling recommended models (may take some time)..." -ForegroundColor Yellow
    
    $models = @("qwen2.5:0.5b", "llama3.2:1b", "llama3.1:8b")
    
    foreach ($model in $models) {
        Write-Host "  → Pulling $model ..." -ForegroundColor Cyan
        ollama pull $model
    }
    
    Write-Host "✓ All models pulled successfully" -ForegroundColor Green
}
catch {
    Write-Host "✗ Ollama not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Ollama first:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://ollama.com/download" -ForegroundColor White
    Write-Host "  2. Download & install for Windows" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
    
    $answer = Read-Host "Open Ollama download page now? (Y/N)"
    if ($answer -eq "Y" -or $answer -eq "y") {
        Start-Process "https://ollama.com/download"
    }
    exit 1
}

# Final message
Write-Host ""
Write-Host "[6/6] Setup finished successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the chatbot you can now run:" -ForegroundColor Yellow
Write-Host "   .\run.ps1" -ForegroundColor White
Write-Host ""
Write-Host "or directly:" -ForegroundColor Yellow
Write-Host "   streamlit run frontend.py" -ForegroundColor White
Write-Host ""

$startNow = Read-Host "Would you like to start the chatbot now? (Y/N)"
if ($startNow -eq "Y" -or $startNow -eq "y") {
    Write-Host ""
    Write-Host "Launching chatbot... (Ctrl+C to stop)" -ForegroundColor Green
    streamlit run frontend.py
}

