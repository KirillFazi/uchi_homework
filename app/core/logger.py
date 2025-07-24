"""Логгер приложения."""
import logging
import sys
from pathlib import Path

from app.core.config import settings


def setup_logger(name: str = "moodle_rag_bot", level: str = "INFO") -> logging.Logger:
    """Настройка логгера."""
    logger = logging.getLogger(name)
    
    # Проверяем, не настроен ли уже логгер
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level.upper()))
    
    # Форматтер
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Консольный хендлер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый хендлер
    log_file = settings.data_dir / "app.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logger() 