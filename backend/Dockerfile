FROM python:3.12

WORKDIR /app

COPY pyproject.toml .
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app app
EOF
