# AI CHEMIST — Python 3.11 + Node.js 22
# PptxGenJS needs Node.js to generate .pptx files from DeepSeek-generated JS code
FROM python:3.11-slim

# ---- System deps + Node.js 22 ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN node --version && npm --version

# ---- PptxGenJS (global, used by pptx_export.py via subprocess) ----
RUN npm install -g pptxgenjs
ENV NODE_PATH=/usr/local/lib/node_modules

# ---- Python dependencies ----
WORKDIR /app
COPY webapp/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Frontend build ----
COPY webapp/frontend/package.json webapp/frontend/package-lock.json* /frontend/
WORKDIR /frontend
RUN npm install
COPY webapp/frontend/ /frontend/
RUN npm run build

# ---- Backend + skill files ----
WORKDIR /app
COPY webapp/backend/ /app/
COPY ppt-design-skill/ /ppt-design-skill/

# ---- Runtime config ----
# SERVE_STATIC=1: backend serves frontend dist/ as static files (production mode)
# PORT: platform-provided (HF Spaces=7860, Zeabur=8080, default=8001)
ENV SERVE_STATIC=1
ENV HOST=0.0.0.0

EXPOSE 8001
EXPOSE 7860

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}
