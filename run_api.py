#!/usr/bin/env python3
"""Скрипт запуска API сервера."""
import uvicorn

from app.core.config import settings
from app.core.logger import logger


def main():
    """Запуск API сервера."""
    logger.info("Запускаем Moodle RAG Chatbot API...")
    
    # Настройка JSON кодировки для правильного отображения Unicode
    import json
    import uvicorn.config
    
    # Переопределяем JSON encoder для uvicorn
    class UnicodeJSONEncoder(json.JSONEncoder):
        def encode(self, obj):
            return super().encode(obj)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Отключаем reload для избежания дублирования
        log_level="warning"  # Уменьшаем уровень логирования uvicorn
    )


if __name__ == "__main__":
    main() 