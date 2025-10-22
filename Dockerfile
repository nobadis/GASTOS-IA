FROM python:3.9-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-minimal.txt .

# Install dependencies without pandas to avoid numpy conflicts
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5100

# Set environment variables
ENV PORT=5100
ENV FLASK_ENV=production

# Run the application
CMD ["python3", "app.py"]
