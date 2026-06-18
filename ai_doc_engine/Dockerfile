FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (build-essential for compiling C extensions if needed)
RUN apt-get update && apt-get install -y build-essential curl

# Install Python dependencies
COPY requirements.txt .
# Install CPU-only PyTorch first to prevent downloading 3GB+ of NVIDIA GPU drivers
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose default port
EXPOSE 8000

# Start Uvicorn directly
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]