FROM python:3.11-slim

# Install system dependencies required by Piper
RUN apt-get update && apt-get install -y \
    espeak-ng \
    libespeak-ng1 \
    libespeak-ng-dev \
    alsa-utils \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make piper executable
RUN chmod +x ./piper

# Expose port
EXPOSE $PORT

# Start command
CMD uvicorn server:app --host 0.0.0.0 --port $PORT
