"""RAG пайплайн для генерации ответов."""
from typing import List, Optional

from app.core.config import settings
from app.core.logger import logger
from app.rag.llm import LangChainLLM
from app.rag.retriever import LangChainRetriever
from app.rag.memory import ConversationMemory
from app.rag.prompts import build_prompt
from app.schemas import ChatRequest, ChatResponse, Source


class LangChainRAGPipeline:
    """RAG пайплайн на основе LangChain."""
    
    def __init__(self):
        self.llm = LangChainLLM()
        self.retriever = LangChainRetriever()
        self.memory = ConversationMemory()
        
        logger.info("RAG пайплайн инициализирован")
    
    def answer(self, request: ChatRequest) -> ChatResponse:
        """Генерирует ответ на основе запроса."""
        try:
            question = request.message
            session_id = request.session_id
            
            logger.info(f"Получен запрос от сессии {session_id}: {question[:50]}...")
            
            # Получаем историю диалога
            history = self.memory.get_history(session_id)
            
            # Ищем релевантные документы
            sources = self.retriever.search(question)
            
            # Получаем контекст
            context = self.retriever.get_context(question)
            
            # Строим промпт с контекстом и историей
            prompt = build_prompt(question, context, history)
            
            # Генерируем ответ
            answer = self.llm.generate(prompt)
            
            # Сохраняем сообщения в историю
            self.memory.add_message(session_id, "user", question)
            self.memory.add_message(session_id, "assistant", answer)
            
            return ChatResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Ошибка в RAG пайплайне: {e}")
            return ChatResponse(
                answer="Произошла ошибка при обработке запроса. Попробуйте позже.",
                sources=[],
                session_id=request.session_id
            )
    

    
    def health_check(self) -> bool:
        """Проверка здоровья всех компонентов."""
        llm_healthy = self.llm.health_check()
        retriever_healthy = self.retriever.health_check()
        
        return llm_healthy and retriever_healthy 