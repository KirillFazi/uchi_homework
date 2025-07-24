"""Основное FastAPI приложение."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.logger import logger


def create_app() -> FastAPI:
    """Создает экземпляр FastAPI приложения."""
    app = FastAPI(
        title="Moodle RAG Chatbot",
        description="RAG чат-бот для документации Moodle",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    

    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене указать конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Подключаем роуты
    app.include_router(router, prefix="/api/v1")
    
    @app.on_event("startup")
    async def startup_event():
        """Событие запуска приложения."""
        logger.info("Moodle RAG Chatbot запускается...")
        logger.info(f"Версия: 0.1.0")
        logger.info(f"Режим отладки: {settings.debug}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Событие остановки приложения."""
        logger.info("Moodle RAG Chatbot останавливается...")
    
    @app.get("/")
    async def root():
        """Корневой эндпоинт."""
        return {
            "message": "Moodle RAG Chatbot API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/api/v1/health"
        }
    
    return app


app = create_app() 