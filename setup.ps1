# ============================================
# Universal Chatbot Setup Script (PowerShell)
# ============================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Universal Chatbot - Setup Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Red
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

# Install Python dependencies
Write-Host ""
Write-Host "[4/6] Installing Python packages..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Python packages installed" -ForegroundColor Green

# Check if Ollama is installed
Write-Host ""
Write-Host "[5/6] Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama found: $ollamaVersion" -ForegroundColor Green
    
    # Pull required models
    Write-Host ""
    Write-Host "Pulling AI models (this may take a while)..." -ForegroundColor Yellow
    
    Write-Host "  → Pulling qwen2.5:0.5b..." -ForegroundColor Cyan
    ollama pull qwen2.5:0.5b
    
    Write-Host "  → Pulling llama3.2:1b..." -ForegroundColor Cyan
    ollama pull llama3.2:1b
    
    Write-Host "  → Pulling llama3.1:8b..." -ForegroundColor Cyan
    ollama pull llama3.1:8b
    
    Write-Host "✓ All models downloaded" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Ollama not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Ollama:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://ollama.ai/download" -ForegroundColor White
    Write-Host "  2. Download and install Ollama for Windows" -ForegroundColor White
    Write-Host "  3. Run this script again" -ForegroundColor White
    Write-Host ""
    
    $install = Read-Host "Do you want to open Ollama download page? (Y/N)"
    if ($install -eq "Y" -or $install -eq "y") {
        Start-Process "https://ollama.ai/download"
    }
    
    exit 1
}

# Setup complete
Write-Host ""
Write-Host "[6/6] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Successful!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the chatbot:" -ForegroundColor Yellow
Write-Host "  1. Make sure Ollama is running (it should auto-start)" -ForegroundColor White
Write-Host "  2. Run: streamlit run frontend.py" -ForegroundColor White
Write-Host ""
Write-Host "Or use the run script:" -ForegroundColor Yellow
Write-Host "  .\run.ps1" -ForegroundColor White
Write-Host ""

# Ask if user wants to start the chatbot now
$start = Read-Host "Do you want to start the chatbot now? (Y/N)"
if ($start -eq "Y" -or $start -eq "y") {
    Write-Host ""
    Write-Host "Starting chatbot..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    streamlit run frontend.py
}

