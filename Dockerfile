# syntax=docker/dockerfile:1.7
ARG BASE_IMAGE=python:3.11-slim
FROM ${BASE_IMAGE}
ARG INSTALL_DEPS=1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    if [ "$INSTALL_DEPS" = "1" ]; then \
      pip install --upgrade pip && \
      pip install --prefer-binary -r requirements.txt; \
    fi

COPY app ./app
COPY web ./web

EXPOSE 8047

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8047"]
