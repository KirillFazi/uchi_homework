"""Схемы данных для API."""
from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    """Источник информации."""
    title: str = Field(..., description="Название документа")
    url: str = Field(..., description="URL документа")
    chunk_id: str = Field(..., description="ID чанка")
    score: float = Field(..., description="Релевантность (0-1)")


class ChatRequest(BaseModel):
    """Запрос на чат."""
    session_id: str = Field(..., description="ID сессии")
    message: str = Field(..., description="Сообщение пользователя")


class ChatResponse(BaseModel):
    """Ответ чат-бота."""
    answer: str = Field(..., description="Ответ бота")
    sources: List[Source] = Field(default=[], description="Источники информации")
    session_id: str = Field(..., description="ID сессии")


class HealthResponse(BaseModel):
    """Ответ проверки здоровья."""
    status: str = Field(..., description="Статус системы")
    message: str = Field(..., description="Сообщение о состоянии") 