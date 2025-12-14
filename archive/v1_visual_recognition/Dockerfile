# Use Python 3.12 slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy project files
COPY . .

# Set environment variable for development mode
ENV FIGURINE_ENV=dev

# Expose any ports if needed (for future web interface)
# EXPOSE 8080

# Default command
CMD ["python", "src/main.py"]
