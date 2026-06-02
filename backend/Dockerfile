FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip
RUN pip install .

COPY app .
COPY alembic.ini .
COPY alembic alembic

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--port", "8000"]
