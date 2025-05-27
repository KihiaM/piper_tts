FROM python:3.9-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libespeak-ng-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and build Piper
RUN git clone https://github.com/rhasspy/piper.git /tmp/piper \
    && cd /tmp/piper \
    && make \
    && cp build/piper /usr/local/bin/ \
    && rm -rf /tmp/piper

# Copy your application
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
