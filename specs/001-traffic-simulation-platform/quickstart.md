# Quickstart Guide: Traffic Simulation Platform

## Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ and Python 3.11+ for local development
- Git for version control

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd traffic-simulation-platform
cp .env.example .env
```

### 2. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (check health)
docker-compose ps
```

This starts:
- PostgreSQL database (port 5432)
- Redis cache (port 6379) 
- Backend API (port 8000)
- Frontend dashboard (port 3000)
- Simulation workers (3 instances)

### 3. Access the Platform
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

### 4. Run Your First Simulation

#### Via Dashboard (Recommended)
1. Open http://localhost:3000
2. Click "Create Persona"
3. Fill in persona details:
   - Name: "Test Visitor"
   - Session Duration: 30-60 seconds
   - Pages: 2-5 pages
   - Click Probability: 60%
4. Click "Create Campaign"
5. Fill in campaign details:
   - Name: "My First Test"
   - Target URL: "https://example.com"
   - Total Sessions: 10
   - Select your persona
6. Click "Start Campaign"
7. Monitor progress in real-time

#### Via CLI (Alternative)
```bash
# Create a persona
./scripts/simulation-cli.py persona create \
  --name "Quick Visitor" \
  --duration-min 10 --duration-max 30 \
  --pages-min 1 --pages-max 3

# Run a quick campaign
./scripts/simulation-cli.py campaign create \
  --name "Quick Test" \
  --target-url "https://httpbin.org" \
  --sessions 5 \
  --persona "Quick Visitor"

# Check results
./scripts/analytics-cli.py campaign analyze --name "Quick Test"
```

### 5. View Results
Navigate to the "Analytics" section in the dashboard to see:
- Session completion rates
- Average page visit times
- Behavioral patterns
- Performance metrics

## Detailed Setup

### Environment Configuration
Edit `.env` file for your environment:

```env
# Database
DATABASE_URL=postgresql://traffic_user:traffic_pass@localhost:5432/traffic_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=traffic_db
DATABASE_USER=traffic_user
DATABASE_PASSWORD=traffic_pass

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
API_WORKERS=4

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXTAUTH_SECRET=your-secret-key-change-in-production
NEXTAUTH_URL=http://localhost:3000

# Simulation Configuration
MAX_CONCURRENT_SESSIONS=100
DEFAULT_RATE_LIMIT_MS=1000
BROWSER_HEADLESS=true
BROWSER_TIMEOUT_MS=30000

# Analytics
ANALYTICS_BATCH_SIZE=1000
ANALYTICS_PROCESSING_INTERVAL=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

#### Worker Development
```bash
cd simulation-workers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start worker in development mode
python -m workers.simulation_worker --debug
```

## User Journey Walkthrough

### 1. Create Your First Persona
A persona defines how simulated users behave:

**Rapid Visitor** (built-in example):
- Session Duration: 10-30 seconds
- Pages Visited: 1-2
- High bounce rate, quick scanning
- Low click-through rate (20%)

**Average Explorer** (built-in example):
- Session Duration: 60-180 seconds  
- Pages Visited: 3-7
- Moderate engagement
- Medium click-through rate (60%)

**Deep Reader** (built-in example):
- Session Duration: 300-600 seconds
- Pages Visited: 5-15
- High engagement, reads content
- High click-through rate (80%)

### 2. Configure Your First Campaign
- **Target URL**: Start with a simple site (avoid heavy JavaScript SPAs initially)
- **Session Count**: Begin with 10-50 sessions for testing
- **Concurrent Limit**: Start with 5-10 concurrent sessions
- **Rate Limiting**: Use default 1000ms delay between actions

### 3. Monitor Progress
- Real-time session counter
- Success/failure rates
- Average completion times
- Live session activity feed

### 4. Analyze Results
- **Behavioral Metrics**: Compare simulated patterns
- **Performance Data**: Resource usage, timing
- **Quality Scores**: How "human-like" the traffic appears
- **Export Data**: CSV/JSON for external analysis

## Validation Tests

Run these tests to verify your setup:

### 1. Health Check Test
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "database": "connected", "redis": "connected"}
```

### 2. API Contract Test
```bash
# Create a test persona
curl -X POST http://localhost:8000/api/v1/personas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Persona",
    "session_duration_min": 10,
    "session_duration_max": 30,
    "pages_min": 1,
    "pages_max": 2
  }'

# List personas
curl http://localhost:8000/api/v1/personas
```

### 3. Frontend Integration Test
```bash
# Check if frontend can reach API
curl http://localhost:3000/api/health
```

### 4. Simulation Test
```bash
# Run a minimal simulation
python scripts/test_simulation.py --quick-test
```

### 5. Database Validation Test
```bash
# Check database schema
python scripts/validate_schema.py
```

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Recreate database
docker-compose down -v && docker-compose up -d postgres
```

**Redis Connection Failed**
```bash
# Check Redis status
docker-compose ps redis

# Test Redis connection
redis-cli -h localhost -p 6379 ping
```

**Simulation Workers Not Starting**
```bash
# Check worker logs
docker-compose logs simulation-worker

# Restart workers
docker-compose restart simulation-worker
```

**Frontend Build Errors**
```bash
# Clear Node.js cache
cd frontend && rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000
```

### Performance Issues

**High Memory Usage**
- Reduce `MAX_CONCURRENT_SESSIONS` in `.env`
- Increase `DEFAULT_RATE_LIMIT_MS` to slow down simulations
- Check Docker memory limits

**Slow Simulations**
- Increase concurrent workers: `docker-compose scale simulation-worker=5`
- Optimize target websites (avoid complex SPAs)
- Use `BROWSER_HEADLESS=true` for better performance

**Database Performance**
- Monitor connection pool usage
- Add database indexes if needed
- Consider partitioning for large datasets

## Next Steps

1. **Custom Personas**: Create personas matching your specific use cases
2. **Target Sites**: Test against your own websites or applications  
3. **Human Baseline**: Collect real user data for comparison
4. **Advanced Analytics**: Set up custom metrics and reports
5. **Integration**: Connect to your existing monitoring tools
6. **Scaling**: Deploy to cloud infrastructure for larger simulations

## Security & Ethics

### Important Guidelines
- **Only test sites you own or have permission to test**
- **Respect robots.txt files** (enabled by default)
- **Use reasonable rate limits** to avoid overwhelming target sites
- **Monitor resource usage** to prevent server overload
- **Keep simulation data secure** and comply with privacy regulations

### Built-in Safeguards
- Rate limiting enforced by default
- robots.txt compliance checking
- Resource usage monitoring
- Automatic session timeouts
- Ethical use warnings in UI

For questions or issues, check the documentation at `/docs/` or create an issue in the project repository.