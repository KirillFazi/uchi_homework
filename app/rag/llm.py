"""Интерфейс для LLM через LangChain."""
from typing import Optional
import logging

from langchain_core.language_models import BaseLLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.core.logger import logger


class LangChainLLM:
    """Интерфейс для LLM через LangChain."""
    
    def __init__(self):
        self.llm = None
        self.is_loaded = False
        self._load_model()
    
    def _load_model(self) -> None:
        """Загружает LLM модель через LangChain."""
        try:
            self.llm = ChatOllama(
                model=settings.llm_model_name,
                temperature=settings.llm_temperature,
                top_p=settings.llm_top_p,
                num_predict=settings.llm_max_tokens,
                stop=["<|im_end|>", "<|endoftext|>", "User:", "Human:", "\n\n"]
            )
            logger.info(f"Загружена Ollama модель: {settings.llm_model_name}")
            
            self.is_loaded = True
            logger.info("LLM модель загружена успешно")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки LLM модели: {e}")
            self.is_loaded = False
    
    def generate(self, prompt: str, max_tokens: int = None, temperature: float = None, top_p: float = None) -> str:
        """Генерирует ответ на основе промпта."""
        if not self.is_loaded or not self.llm:
            return self._fallback_response(prompt)
        
        try:
            # Формируем промпт для модели
            formatted_prompt = self._format_prompt(prompt)
            
            # Генерируем ответ
            response = self.llm.invoke(formatted_prompt)
            
            # Извлекаем текст ответа
            if hasattr(response, 'content'):
                answer = response.content
            elif hasattr(response, 'text'):
                answer = response.text
            else:
                answer = str(response)
            
            logger.debug(f"LLM сгенерировал ответ длиной {len(answer)} символов")
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return self._fallback_response(prompt)
    
    def _format_prompt(self, prompt: str) -> str:
        """Форматирует промпт для модели."""
        # Системный промпт для RAG
        system_prompt = """Ты — помощник по Moodle. Твоя задача — давать конкретные, практические инструкции.

ВАЖНЫЕ ПРАВИЛА:
1. Давай конкретные пошаговые инструкции, а не общие фразы
2. Используй форматированный вывод (шаги, буллеты, списки)
3. Отвечай на русском языке, если вопрос задан на русском
4. Будь точным и конкретным

ФОРМАТ ОТВЕТА:
1. Краткий ответ на вопрос
2. Конкретные пошаговые инструкции (если применимо)
3. Практические советы

ВОПРОС: {prompt}

ОТВЕТ:"""
        
        return system_prompt.format(prompt=prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback ответ, если LLM недоступна."""
        return ("Я не могу найти точную информацию по вашему запросу в доступной документации. "
               "Рекомендую обратиться к официальной документации Moodle или уточнить вопрос. "
               "Для получения более точных ответов убедитесь, что у вас загружена LLM модель.")
    
    def health_check(self) -> bool:
        """Проверка здоровья LLM."""
        if not self.is_loaded:
            logger.warning("LLM не загружена, но fallback режим доступен")
            return True  # Fallback доступен
        
        try:
            # Простой тест генерации
            test_response = self.generate("Test", max_tokens=10)
            return len(test_response) > 0
        except Exception as e:
            logger.error(f"LLM не здоров: {e}")
            return False 