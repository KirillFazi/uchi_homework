"""API маршруты для чат-бота."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.rag.pipeline import LangChainRAGPipeline
from app.schemas import ChatRequest, ChatResponse, HealthResponse

# Создаем роутер
router = APIRouter(tags=["chat"])

# Глобальный экземпляр пайплайна
rag_pipeline = LangChainRAGPipeline()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Обрабатывает чат-запрос."""
    try:
        # Генерируем ответ через RAG пайплайн
        response = rag_pipeline.answer(request)
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Проверка состояния системы."""
    try:
        # Проверяем здоровье пайплайна
        is_healthy = rag_pipeline.health_check()
        
        status = "healthy" if is_healthy else "unhealthy"
        
        return HealthResponse(
            status=status,
            message="Moodle RAG Chatbot работает" if is_healthy else "Проблемы с системой"
        )
        
    except Exception as e:
        logger.error(f"Ошибка проверки здоровья: {e}")
        return HealthResponse(
            status="unhealthy",
            message=f"Ошибка проверки здоровья: {str(e)}"
        ) 