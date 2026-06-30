FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and frontend
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose server port
EXPOSE 5000

# Run Flask backend on startup
ENV PORT=5000
CMD ["python", "backend/app.py"]
