FROM python:3.11-slim

# 1. Dépendances système (root)
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates \
    libnss3 libnspr4 libatk-bridge2.0-0 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libxss1 libxshmfence1 libdrm2 libxkbcommon0 \
    libgtk-3-0 libgbm1 libasound2 \
    fontconfig fonts-unifont fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

# 2. Installer playwright + dépendances système du navigateur (toujours root)
RUN pip install --no-cache-dir playwright \
 && playwright install-deps chromium

# 3. Créer l'utilisateur appuser
RUN useradd -m -u 1000 appuser

# 4. Basculer sur appuser
USER appuser
WORKDIR /app

# 5. Copier requirements et installer dans /home/appuser/.local
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 6. Télécharger Chromium dans le cache de appuser
RUN /home/appuser/.local/bin/playwright install chromium

# 7. Copier le code
COPY --chown=appuser:appuser . .

# 8. PATH pour les scripts Python et Playwright
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH=/app/src
ENV BROWSER_HEADLESS=true

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD python -c "import redis; import os; redis.Redis.from_url(os.environ.get('REDIS_URL','redis://localhost:6379')).ping()" || exit 1

# Default command (use shell for env var expansion inside container)
CMD ["sh", "-lc", "cd /app/src && python workers/simple_worker.py"]
