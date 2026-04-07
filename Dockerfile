FROM python:3.10-slim

# Install C++ compiler and build tools
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set default environment variables for inference
ENV API_BASE_URL="https://api.openai.com/v1"
ENV MODEL_NAME="gpt-4o-mini"
# Expose port for HF Space
EXPOSE 7860

# Run inference with Flask server for HF Space validator
CMD ["python", "app.py"]