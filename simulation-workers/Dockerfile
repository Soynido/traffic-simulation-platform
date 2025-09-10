FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install system deps required by Chromium (Debian trixie names)
RUN apt-get update && apt-get install -y \
    libnss3 libnspr4 \
    libatk-bridge2.0-0 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libxss1 libxshmfence1 libdrm2 libxkbcommon0 \
    libgtk-3-0 libgbm1 libasound2 \
    fontconfig fonts-unifont fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers
RUN playwright install chromium

# Copy project files
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONPATH=/app/src
ENV BROWSER_HEADLESS=true

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import redis; import os; redis.Redis.from_url(os.environ.get('REDIS_URL','redis://localhost:6379')).ping()" || exit 1

# Default command (use shell for env var expansion inside container)
CMD ["sh", "-lc", "cd /app/src && python workers/simulation_worker.py --worker-id \"${WORKER_ID:-worker-1}\" --database-url \"${DATABASE_URL}\" --redis-url \"${REDIS_URL}\""]
