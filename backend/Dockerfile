FROM python:3.11-slim

WORKDIR /app

# Install build tools
RUN pip install --upgrade pip
RUN pip install "setuptools>=68.0.0,<70.0.0" "wheel>=0.41.0"

# Copy requirements and pyproject.toml
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of your code
COPY . .

# Set the default command (adjust as needed)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
