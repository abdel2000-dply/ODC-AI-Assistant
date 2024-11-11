# Use a lightweight Python image compatible with Raspberry Pi's ARM architecture
FROM arm32v7/python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install any system dependencies (e.g., ALSA for audio support, dependencies for speech recognition)
RUN apt-get update && \
    apt-get install -y \
    libasound2-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set the environment variable to avoid potential issues with buffering in Python
ENV PYTHONUNBUFFERED=1

# Define the default command to run your app
CMD ["python", "src/main.py"]
