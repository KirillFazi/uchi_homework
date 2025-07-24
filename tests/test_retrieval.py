"""Тесты для retriever."""
import pytest
import numpy as np
from unittest.mock import Mock, patch

from app.rag.retriever import LangChainRetriever
from app.schemas import Source


class TestLangChainRetriever:
    """Тесты для LangChainRetriever."""
    
    @pytest.fixture
    def mock_chroma_client(self):
        """Мок для Chroma клиента."""
        with patch('app.rag.retriever.chromadb.Client') as mock_client:
            # Мокаем коллекцию
            mock_collection = Mock()
            mock_collection.count.return_value = 100
            
            # Мокаем результаты поиска
            mock_collection.query.return_value = {
                "documents": [["Test document content"]],
                "metadatas": [[{"title": "Test Page", "url": "https://test.com"}]],
                "distances": [[0.1]],
                "ids": [["test_chunk_1"]]
            }
            
            mock_collection.get.return_value = {
                "documents": ["Test document content"]
            }
            
            mock_client.return_value.get_collection.return_value = mock_collection
            yield mock_client
    
    @pytest.fixture
    def mock_embedding_model(self):
        """Мок для модели эмбеддингов."""
        with patch('app.rag.retriever.HuggingFaceEmbeddings') as mock_model:
            mock_instance = Mock()
            # Создаем numpy array для эмбеддинга
            mock_instance.encode.return_value = np.array([[0.1, 0.2, 0.3]])
            mock_model.return_value = mock_instance
            yield mock_model
    
    def test_retriever_initialization(self, mock_chroma_client, mock_embedding_model):
        """Тест инициализации retriever."""
        retriever = LangChainRetriever()
        assert retriever is not None
        assert retriever.collection is not None
        assert retriever.embedding_model is not None
    
    def test_search_returns_sources(self, mock_chroma_client, mock_embedding_model):
        """Тест поиска возвращает источники."""
        retriever = LangChainRetriever()
        sources = retriever.search("test query")
        
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert all(isinstance(source, Source) for source in sources)
        
        # Проверяем структуру Source
        source = sources[0]
        assert hasattr(source, 'title')
        assert hasattr(source, 'url')
        assert hasattr(source, 'chunk_id')
        assert hasattr(source, 'score')
    
    def test_get_document_text(self, mock_chroma_client, mock_embedding_model):
        """Тест получения текста документа."""
        retriever = LangChainRetriever()
        text = retriever.get_document_text("test_chunk_1")
        
        assert text is not None
        assert isinstance(text, str)
        assert "Test document content" in text
    
    def test_get_context(self, mock_chroma_client, mock_embedding_model):
        """Тест получения контекста."""
        retriever = LangChainRetriever()
        context = retriever.get_context("test query")
        
        assert isinstance(context, str)
        assert len(context) > 0
        assert "Test Page" in context
    
    def test_health_check(self, mock_chroma_client, mock_embedding_model):
        """Тест проверки здоровья."""
        retriever = LangChainRetriever()
        is_healthy = retriever.health_check()
        
        assert isinstance(is_healthy, bool)
        assert is_healthy  # Должен быть здоров с моком
    
    def test_search_with_empty_results(self, mock_chroma_client, mock_embedding_model):
        """Тест поиска с пустыми результатами."""
        # Мокаем пустые результаты
        mock_collection = Mock()
        mock_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "ids": [[]]
        }
        mock_chroma_client.return_value.get_collection.return_value = mock_collection
        
        retriever = LangChainRetriever()
        sources = retriever.search("test query")
        
        assert isinstance(sources, list)
        assert len(sources) == 0
    
    def test_search_exception_handling(self, mock_chroma_client, mock_embedding_model):
        """Тест обработки исключений при поиске."""
        # Мокаем исключение
        mock_collection = Mock()
        mock_collection.query.side_effect = Exception("Test error")
        mock_chroma_client.return_value.get_collection.return_value = mock_collection
        
        retriever = LangChainRetriever()
        sources = retriever.search("test query")
        
        assert isinstance(sources, list)
        assert len(sources) == 0  # Должен вернуть пустой список при ошибке 