FROM python:3.11-slim

# Install system utilities, git, and Node.js for polyglot testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install backend Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application source
COPY backend ./backend
COPY sample-project ./sample-project

# Pre-install sample-project npm dependencies so it works out-of-the-box
WORKDIR /app/sample-project
RUN npm install

WORKDIR /app/backend

ENV PYTHONPATH=/app/backend
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
