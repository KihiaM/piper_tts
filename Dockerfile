FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download static Piper binary
RUN wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz \
    && tar -xzf piper_linux_x86_64.tar.gz \
    && mv piper/piper /usr/local/bin/ \
    && chmod +x /usr/local/bin/piper \
    && rm -rf piper_linux_x86_64.tar.gz piper/

# Copy your application
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
