#!/bin/bash

# Development setup script for Traffic Simulation Platform
# Sets up the development environment from scratch

set -e

echo "🚀 Traffic Simulation Platform - Development Setup"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"

# Setup environment
echo -e "${YELLOW}🔧 Setting up environment...${NC}"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

# Install backend dependencies
echo -e "${YELLOW}🐍 Installing backend dependencies...${NC}"
cd backend
python -m pip install -r requirements.txt
cd ..
echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Install frontend dependencies
echo -e "${YELLOW}⚛️  Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

# Install simulation workers dependencies
echo -e "${YELLOW}🎭 Installing simulation workers dependencies...${NC}"
cd simulation-workers
python -m pip install -r requirements.txt
echo -e "${YELLOW}Installing Playwright browsers...${NC}"
playwright install chromium
cd ..
echo -e "${GREEN}✅ Simulation workers dependencies installed${NC}"

# Start infrastructure services
echo -e "${YELLOW}🐳 Starting infrastructure services...${NC}"
docker-compose up -d postgres redis
echo -e "${GREEN}✅ Infrastructure services started${NC}"

# Wait for services
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Initialize database
echo -e "${YELLOW}🗄️  Initializing database...${NC}"
cd backend
# Note: We'll add Alembic migrations in later tasks
# For now, just check connection
python -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    try:
        conn = await asyncpg.connect(
            'postgresql://traffic_user:traffic_pass@localhost:5432/traffic_db'
        )
        await conn.close()
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        exit(1)

asyncio.run(test_connection())
"
cd ..

# Final health check
echo -e "${YELLOW}🔍 Running health check...${NC}"
./scripts/health-check.sh

echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Run 'make dev' to start all development servers"
echo "2. Open http://localhost:3001 for the dashboard"
echo "3. Open http://localhost:8000/docs for the API documentation"
echo ""
echo "Useful commands:"
echo "  make dev      - Start development servers"
echo "  make test     - Run all tests"
echo "  make lint     - Run code linting"
echo "  make health   - Check service health"