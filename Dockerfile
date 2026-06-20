# AI CHEMIST — Python 3.11 + Node.js 22
# PptxGenJS needs Node.js to generate .pptx files from DeepSeek-generated JS code
FROM python:3.11-slim

# ---- System deps + Node.js 22 ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && node --version && npm --version

# ---- PptxGenJS (global, used by pptx_export.py via subprocess) ----
RUN npm install -g pptxgenjs
ENV NODE_PATH=/usr/local/lib/node_modules

# ---- Python dependencies ----
WORKDIR /app
COPY webapp/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Frontend build ----
WORKDIR /frontend
COPY webapp/frontend/package.json webapp/frontend/package-lock.json ./
RUN npm install
COPY webapp/frontend/ ./
RUN npm run build
# 验证构建产物存在
RUN ls -la /frontend/dist/ && test -f /frontend/dist/index.html || (echo "ERROR: frontend build failed" && exit 1)

# ---- Backend + skill files ----
WORKDIR /app
COPY webapp/backend/ /app/
COPY ppt-design-skill/ /ppt-design-skill/

# ---- Startup script ----
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'set -e' >> /start.sh && \
    echo 'PORT=${PORT:-8001}' >> /start.sh && \
    echo 'echo "=== AI CHEMIST starting ==="' >> /start.sh && \
    echo 'echo "PORT=$PORT"' >> /start.sh && \
    echo 'echo "SERVE_STATIC=$SERVE_STATIC"' >> /start.sh && \
    echo 'echo "Python: $(python --version)"' >> /start.sh && \
    echo 'echo "Node: $(node --version)"' >> /start.sh && \
    echo 'ls -la /app/main.py && echo "main.py OK"' >> /start.sh && \
    echo 'ls -la /frontend/dist/index.html && echo "frontend dist OK"' >> /start.sh && \
    echo 'ls -d /ppt-design-skill && echo "skill dir OK"' >> /start.sh && \
    echo 'echo "Starting uvicorn on 0.0.0.0:$PORT..."' >> /start.sh && \
    echo 'exec uvicorn main:app --host 0.0.0.0 --port $PORT' >> /start.sh && \
    chmod +x /start.sh

# ---- Runtime config ----
ENV SERVE_STATIC=1
ENV FRONTEND_DIST=/frontend/dist

EXPOSE 8001 8080

CMD ["/bin/bash", "/start.sh"]
