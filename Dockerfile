FROM python:3.9-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-basic.txt .

# Install only basic dependencies
RUN pip install --no-cache-dir -r requirements-basic.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5100

# Set environment variables
ENV PORT=5100
ENV FLASK_ENV=production

# Run the application
CMD ["python3", "app.py"]
