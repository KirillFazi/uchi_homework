"""Модуль для перевода запросов."""
import logging
from typing import Optional

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
except ImportError:
    torch = None
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None

logger = logging.getLogger(__name__)


class QueryTranslator:
    """Переводчик запросов с использованием предобученной модели."""
    
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._is_initialized = False
        
    def _initialize_model(self):
        """Инициализирует модель перевода."""
        try:
            # Проверяем, что transformers доступен
            if AutoTokenizer is None or AutoModelForSeq2SeqLM is None:
                raise ImportError("transformers не установлен")
            
            # Используем модель MarianMT для перевода русский -> английский
            model_name = "Helsinki-NLP/opus-mt-ru-en"
            
            logger.info(f"Загружаем модель перевода: {model_name}")
            
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            self._is_initialized = True
            logger.info("Модель перевода загружена успешно")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки модели перевода: {e}")
            logger.info("Используем fallback переводчик")
            self._is_initialized = False
    
    def translate(self, text: str, source_lang: str = "ru", target_lang: str = "en") -> str:
        """Переводит текст с использованием предобученной модели.
        
        Args:
            text: Текст для перевода
            source_lang: Исходный язык (по умолчанию русский)
            target_lang: Целевой язык (по умолчанию английский)
            
        Returns:
            Переведенный текст
        """
        if not text or not text.strip():
            return text
            
        # Если это не русский текст, возвращаем как есть
        if not self._is_russian_text(text):
            return text
            
        # Инициализируем модель при первом использовании
        if not self._is_initialized:
            self._initialize_model()
            
        # Если модель не загрузилась, используем fallback
        if not self._is_initialized:
            return self._fallback_translate(text)
            
        try:
            # Токенизируем текст
            inputs = self._tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            
            # Генерируем перевод
            with torch.no_grad():
                outputs = self._model.generate(**inputs, max_length=512)
            
            # Декодируем результат
            translated = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.debug(f"Переведен запрос: '{text}' -> '{translated}'")
            return translated
            
        except Exception as e:
            logger.error(f"Ошибка перевода: {e}")
            return self._fallback_translate(text)
    
    def _is_russian_text(self, text: str) -> bool:
        """Проверяет, содержит ли текст русские символы."""
        return any(ord(char) > 127 for char in text)
    
    def _fallback_translate(self, query: str) -> str:
        """Fallback переводчик с использованием словаря."""
        # Простой словарь переводов для ключевых слов
        translations = {
            # Создание курса
            "создать": "create",
            "добавить": "add",
            "новый": "new",
            "курс": "course",
            "курсы": "courses",
            
            # Настройки
            "настроить": "configure",
            "настройка": "configuration",
            "система": "system",
            "оценки": "grades",
            "оценка": "grade",
            
            # Пользователи
            "пользователь": "user",
            "пользователи": "users",
            "активность": "activity",
            "журнал": "log",
            "журналы": "logs",
            "просмотреть": "view",
            
            # Общие слова
            "как": "how to",
            "что": "what",
            "где": "where",
            "когда": "when",
            "почему": "why"
        }
        
        # Простой перевод по словарю
        translated_query = query.lower()
        for ru_word, en_word in translations.items():
            translated_query = translated_query.replace(ru_word, en_word)
        
        # Если запрос содержит русские символы, добавляем английские ключевые слова
        if self._is_russian_text(query):
            # Добавляем общие английские ключевые слова для Moodle
            moodle_keywords = ["moodle", "course", "user", "admin", "settings"]
            for keyword in moodle_keywords:
                if keyword not in translated_query:
                    translated_query += f" {keyword}"
        
        logger.debug(f"Fallback перевод: '{query}' -> '{translated_query}'")
        return translated_query


# Глобальный экземпляр переводчика
translator = QueryTranslator() 