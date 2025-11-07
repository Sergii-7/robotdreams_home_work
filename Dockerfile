FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# Робоча директорія додатку
WORKDIR /app

# ---- Кешування залежностей (lockfile-based) ----
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---- Код застосунку ----
COPY . .
RUN uv sync --frozen --no-dev

# Корисні env
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Точка монтування для зберігання файлів
RUN mkdir -p /app/src/file_storage
VOLUME ["/app/src/file_storage"]

# Відкритий порт
EXPOSE 8081

# Опціональні параметри Gunicorn
ENV WEB_CONCURRENCY=2 \
    GUNICORN_TIMEOUT=60

# Запуск Gunicorn через uv
CMD ["uv", "run", "gunicorn", "-b", "0.0.0.0:8081", "main:app"]
