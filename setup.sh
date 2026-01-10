#!/usr/bin/env bash

# ============================================
# Universal Chatbot Setup Script (Linux/macOS)
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "================================================"
echo -e "${CYAN}  Universal Chatbot - Setup Script${NC}"
echo "================================================"
echo ""

# 1. Python check
echo -e "${YELLOW}→ Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found!${NC}"
    echo "Please install Python 3.8 or newer"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"

# 2. Virtual environment
echo ""
echo -e "${YELLOW}→ Creating/using virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# 3. Activate venv
echo ""
echo -e "${YELLOW}→ Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Activated${NC}"

# 4. Install dependencies
echo ""
echo -e "${YELLOW}→ Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# 5. Ollama check & model pull
echo ""
echo -e "${YELLOW}→ Checking Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}✗ Ollama not found!${NC}"
    echo "Please install Ollama: https://ollama.com/download"
    exit 1
fi

echo -e "${GREEN}✓ Ollama is installed${NC}"

echo ""
echo -e "${YELLOW}→ Pulling models (may take a while)...${NC}"
MODELS=("qwen2.5:0.5b" "llama3.2:1b" "llama3.1:8b")

for model in "${MODELS[@]}"; do
    echo -e "  → $model"
    ollama pull "$model" > /dev/null 2>&1
    echo -e "     ${GREEN}done${NC}"
done

echo -e "${GREEN}✓ All models ready${NC}"

echo ""
echo -e "${GREEN}================================================"
echo "          Setup finished successfully!"
echo "================================================"
echo -e "${NC}"
echo -e "You can now start the chatbot with:"
echo -e "   ${YELLOW}./run.sh${NC}"
echo ""
echo -e "or directly:"
echo -e "   ${YELLOW}streamlit run frontend.py${NC}"
echo ""


