FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Установка Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Установка Poetry
RUN pip install poetry

# Настройка Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p data/{raw,chunks,chroma} models

# Порт
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Запуск Ollama в фоне и API
CMD ["sh", "-c", "ollama serve & sleep 10 && poetry run python run_api.py"] 