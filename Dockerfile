FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies including piper-tts
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code and your trained model
COPY . .

# No need to create voices directory since you have your own model

# Expose port (adjust if your app uses a different port)
EXPOSE 8000

# Start the server
CMD ["python", "server.py"]
