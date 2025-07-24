"""Конфигурация приложения."""
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Пути к данным
    data_dir: Path = Field(default=Path("data"), description="Корневая папка с данными")
    raw_dir: Path = Field(default=Path("data/raw"), description="Папка с исходными данными")
    chunks_dir: Path = Field(default=Path("data/chunks"), description="Папка с чанками")
    chroma_dir: Path = Field(default=Path("data/chroma"), description="Папка Chroma DB")
    models_dir: Path = Field(default=Path("models"), description="Папка с моделями")
    
    # Moodle API
    moodle_api_url: str = Field(
        default="https://docs.moodle.org/403/en/api.php",
        description="URL MediaWiki API Moodle"
    )
    moodle_version: str = Field(default="403", description="Версия Moodle")
    moodle_lang: str = Field(default="en", description="Язык документации")
    
    # Chroma DB
    collection_name: str = Field(default="moodle_docs", description="Имя коллекции Chroma")
    
    # Embeddings
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Модель для эмбеддингов"
    )
    chunk_size: int = Field(default=1000, description="Размер чанка в символах")
    chunk_overlap: int = Field(default=100, description="Перекрытие чанков")
    
    # LLM (LangChain)
    llm_provider: str = Field(default="ollama", description="Провайдер LLM (ollama, openai, etc.)")
    llm_model_name: str = Field(default="qwen2.5:7b", description="Название модели LLM")
    llm_base_url: Optional[str] = Field(default=None, description="Base URL для LLM API")
    llm_api_key: Optional[str] = Field(default=None, description="API ключ для LLM")
    llm_max_tokens: int = Field(default=4096, description="Максимум токенов для генерации")
    llm_temperature: float = Field(default=0.3, description="Температура генерации")
    llm_top_p: float = Field(default=0.9, description="Top-p параметр для генерации")
    
    # RAG
    top_k: int = Field(default=5, description="Количество релевантных документов")
    use_reranker: bool = Field(default=True, description="Использовать reranker")
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Модель для reranker"
    )
    
    # API
    host: str = Field(default="0.0.0.0", description="Хост для API")
    port: int = Field(default=8000, description="Порт для API")
    debug: bool = Field(default=False, description="Режим отладки")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __post_init__(self):
        """Создаем необходимые директории."""
        for path in [self.data_dir, self.raw_dir, self.chunks_dir, self.chroma_dir, self.models_dir]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings() 