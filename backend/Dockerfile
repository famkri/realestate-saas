cat > Dockerfile <<EOF
FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app app
EOF