"""Retriever для поиска релевантных документов через LangChain."""
from typing import List, Optional
import chromadb
from chromadb.config import Settings

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.core.config import settings
from app.core.logger import logger
from app.core.translator import translator
from app.schemas import Source


class LangChainRetriever:
    """Retriever для поиска в ChromaDB через LangChain."""
    
    def __init__(self):
        self.chroma_dir = settings.chroma_dir
        self.collection_name = settings.collection_name
        self.top_k = settings.top_k
        self.vectorstore = None
        self.embeddings = None
        self.retriever = None
        
        self._init_embeddings()
        self._init_vectorstore()
    
    def _init_embeddings(self) -> None:
        """Инициализирует модель эмбеддингов."""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            logger.info(f"Загружена модель эмбеддингов: {settings.embedding_model}")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели эмбеддингов: {e}")
            raise
    
    def _init_vectorstore(self) -> None:
        """Инициализирует векторное хранилище."""
        try:
            self.vectorstore = Chroma(
                persist_directory=str(self.chroma_dir),
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            
            # Создаем базовый retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.top_k}
            )
            
            logger.info(f"Инициализирован ChromaDB retriever для коллекции {self.collection_name}")
        except Exception as e:
            logger.error(f"Ошибка инициализации векторного хранилища: {e}")
            raise
    
    def search(self, query: str) -> List[Source]:
        """Ищет релевантные документы."""
        try:
            # Переводим запрос на английский для лучшего поиска
            translated_query = translator.translate(query)

            # Получаем документы через LangChain retriever
            documents = self.retriever.get_relevant_documents(translated_query)
            
            # Преобразуем в Source объекты
            sources = []
            for i, doc in enumerate(documents):
                # Извлекаем метаданные
                metadata = doc.metadata
                title = metadata.get("title", f"Document {i+1}")
                chunk_id = metadata.get("chunk_id", f"chunk_{i}")
                
                # Используем URL из метаданных
                url = metadata.get("url", "")
                
                # Простой score на основе позиции (можно улучшить)
                score = 1.0 - (i * 0.1)
                
                source = Source(
                    title=title,
                    url=url,
                    chunk_id=chunk_id,
                    score=score
                )
                sources.append(source)
            
            return sources
            
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []
    
    def get_context(self, query: str) -> str:
        """Получает контекст из найденных документов."""
        try:
            # Переводим запрос на английский для лучшего поиска
            translated_query = translator.translate(query)
            documents = self.retriever.get_relevant_documents(translated_query)
            
            if not documents:
                return ""
            
            context_parts = []
            for i, doc in enumerate(documents, 1):
                metadata = doc.metadata
                title = metadata.get("title", f"Document {i}")
                content = doc.page_content
                
                # Ограничиваем длину контента для лучшего качества
                if len(content) > 1000:
                    content = content[:1000] + "..."
                
                context_parts.append(f"=== ДОКУМЕНТ {i}: {title} ===\n{content}\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Ошибка получения контекста: {e}")
            return ""
    

    
    def health_check(self) -> bool:
        """Проверка здоровья retriever."""
        try:
            # Простой тест поиска
            test_results = self.search("test")
            return True
        except Exception as e:
            logger.error(f"Retriever не здоров: {e}")
            return False 