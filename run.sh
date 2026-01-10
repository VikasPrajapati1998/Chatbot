#!/usr/bin/env bash

# ============================================
# Universal Chatbot - Run Script (Linux/macOS)
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "================================================"
echo -e "${CYAN}  Starting Universal Chatbot...${NC}"
echo "================================================"
echo ""

# Check venv
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo -e "Please run ${YELLOW}./setup.sh${NC} first"
    exit 1
fi

# Activate venv
echo -e "${YELLOW}→ Activating virtual environment...${NC}"
source venv/bin/activate

# Check/start Ollama
echo -e "${YELLOW}→ Checking Ollama...${NC}"
if pgrep -x "ollama" > /dev/null; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${YELLOW}→ Starting Ollama in background...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 3
    echo -e "${GREEN}✓ Ollama started${NC}"
fi

echo ""
echo -e "${GREEN}✓ Starting chatbot at http://localhost:8501${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo "================================================"
echo ""

streamlit run frontend.py


