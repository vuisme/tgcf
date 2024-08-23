# Stage 1: Build
FROM python:3.10-slim AS builder
WORKDIR /app
COPY . .
RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils ffmpeg tesseract-ocr && \
    apt-get autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
RUN python -m venv /venv && \
    . /venv/bin/activate && \
    pip install --upgrade pip wheel setuptools && \
    pip install poetry && \
    poetry install --no-dev

# Stage 2: Production
FROM python:3.10-slim
ENV VENV_PATH="/venv"
ENV PATH="$VENV_PATH/bin:$PATH"
WORKDIR /app
COPY --from=builder /app /app
COPY --from=builder /venv /venv
EXPOSE 8501
CMD tgcf-web

