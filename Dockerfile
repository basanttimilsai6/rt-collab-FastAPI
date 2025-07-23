FROM docker.io/python:3.12-slim AS base
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock* /app/


RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

COPY . .