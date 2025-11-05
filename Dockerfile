# ---- Base with Python + uv ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# Робоча директорія додатку
WORKDIR /app

# Кеш залежностей
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Код
COPY . .
RUN uv sync --frozen --no-dev

# Корисні env для контейнера
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Точка монтування для бази даних
RUN mkdir -p app/src/db
VOLUME ["/app/src/db"]

# Відкритий порт для додатку
EXPOSE 8081

# Запуск стартового скрипта
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["./start.sh"]
