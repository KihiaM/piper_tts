FROM rhasspy/piper:latest

# Copy your application files
COPY . /app
WORKDIR /app

# Install any additional dependencies you need
# RUN pip install -r requirements.txt

# Your startup command
CMD ["your-startup-command"]
