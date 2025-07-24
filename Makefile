.PHONY: help install setup fetch chunk ingest test run clean

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	poetry install

setup: ## Настройка проекта (создание директорий)
	mkdir -p data/{raw,chunks,chroma} models
	@echo "Убедитесь, что Ollama установлен и запущен:"
	@echo "  brew install ollama  # macOS"
	@echo "  brew services start ollama  # macOS"
	@echo "  ollama pull qwen2.5:7b  # Скачать модель"

fetch: ## Загрузить документацию Moodle
	poetry run fetch-docs

chunk: ## Разбить документы на чанки
	poetry run chunk-docs

ingest: ## Загрузить чанки в ChromaDB
	poetry run ingest-chroma

pipeline: ## Полный пайплайн: fetch + chunk + ingest
	$(MAKE) fetch
	$(MAKE) chunk
	$(MAKE) ingest

test: ## Запустить тесты
	pytest

test-cov: ## Запустить тесты с покрытием
	pytest --cov=app --cov-report=html

eval: ## Запустить тестирование RAG системы
	poetry run eval-run

run: ## Запустить API сервер
	poetry run python run_api.py

run-dev: ## Запустить API в режиме разработки
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

format: ## Форматировать код
	black .
	isort .

lint: ## Проверить код линтером
	flake8 app/
	mypy app/

pre-commit: ## Запустить pre-commit hooks
	pre-commit run --all-files

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov

clean-data: ## Очистить данные (осторожно!)
	rm -rf data/chroma/*
	rm -rf data/chunks/*
	rm -rf data/raw/*

docker-build: ## Собрать Docker образ
	docker build -t moodle-rag-bot .

docker-run: ## Запустить в Docker
	docker-compose up -d

docker-stop: ## Остановить Docker контейнеры
	docker-compose down

docker-logs: ## Показать логи Docker
	docker-compose logs -f

all: setup install pipeline ## Полная установка и настройка 