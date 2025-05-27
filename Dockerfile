FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Install Piper
RUN wget -O /tmp/piper.deb https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_2023.11.14-2_amd64.deb \
    && dpkg -i /tmp/piper.deb || apt-get install -f -y \
    && rm /tmp/piper.deb

# Copy your application
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]

# Add debugging info
RUN echo "=== Checking piper binary ===" \
    && ls -la ./piper \
    && echo "=== Checking library dependencies ===" \
    && ldd ./piper || echo "ldd failed" \
    && echo "=== Searching for libpiper_phonemize ===" \
    && find / -name "*piper_phonemize*" 2>/dev/null || echo "Not found" \
    && echo "=== Library cache ===" \
    && ldconfig -p | grep -i piper || echo "No piper libs in cache"
