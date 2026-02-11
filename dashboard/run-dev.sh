#!/bin/bash

# Development Run Script for Brent Oil Dashboard

echo "Starting Brent Oil Dashboard in development mode..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to kill processes on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}Starting backend server...${NC}"
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting frontend server...${NC}"
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}✅ Both servers are running!${NC}"
echo -e "\nAccess the dashboard at: ${YELLOW}http://localhost:3000${NC}"
echo -e "Backend API at: ${YELLOW}http://localhost:5000${NC}"
echo -e "\nPress Ctrl+C to stop both servers"

# Keep script running
wait $BACKEND_PID $FRONTEND_PID