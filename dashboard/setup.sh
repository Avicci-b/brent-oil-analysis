#!/bin/bash

# Brent Oil Dashboard Setup Script
echo "Setting up Brent Oil Price Analysis Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Python
if command -v python3 &>/dev/null; then
    echo -e "${GREEN}✓ Python 3 is installed${NC}"
else
    echo -e "${RED}✗ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check Node.js
if command -v node &>/dev/null; then
    echo -e "${GREEN}✓ Node.js is installed${NC}"
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    if [[ $(echo "$NODE_VERSION 16.0" | awk '{print ($1 >= $2)}') -eq 1 ]]; then
        echo -e "${GREEN}✓ Node.js version $NODE_VERSION is compatible${NC}"
    else
        echo -e "${YELLOW}⚠ Node.js version $NODE_VERSION may have compatibility issues${NC}"
    fi
else
    echo -e "${RED}✗ Node.js is required but not installed${NC}"
    exit 1
fi

# Check npm
if command -v npm &>/dev/null; then
    echo -e "${GREEN}✓ npm is installed${NC}"
else
    echo -e "${RED}✗ npm is required but not installed${NC}"
    exit 1
fi

# Setup Backend
echo -e "\n${YELLOW}Setting up backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if data files exist
echo -e "\n${YELLOW}Checking for required data files...${NC}"
if [ -f "../../data/processed/brent_clean.csv" ]; then
    echo -e "${GREEN}✓ Price data found${NC}"
else
    echo -e "${YELLOW}⚠ Price data not found. Run Task 2 analysis first.${NC}"
fi

if [ -f "../../data/processed/historical_events.csv" ]; then
    echo -e "${GREEN}✓ Events data found${NC}"
else
    echo -e "${YELLOW}⚠ Events data not found. Run Task 1 first.${NC}"
fi

deactivate
cd ..

# Setup Frontend
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

echo -e "\n${GREEN}✅ Setup completed successfully!${NC}"

# Display next steps
echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2. Start the frontend server (in a new terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Open your browser and go to:"
echo "   http://localhost:3000"
echo ""
echo "4. For Docker deployment:"
echo "   docker-compose up --build"