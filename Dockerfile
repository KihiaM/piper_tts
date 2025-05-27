FROM python:3.9-slim

COPY . /app
WORKDIR /app

# Install piper-tts Python package
RUN pip install piper-tts torch torchaudio

CMD ["python", "app.py"]
