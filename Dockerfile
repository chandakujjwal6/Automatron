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

# Command to run your evaluation or a simple UI
CMD ["python", "evaluate_agent.py"]