#!/usr/bin/env python3
"""Скрипт для загрузки чанков в ChromaDB."""
import sys
import pathlib

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import time
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from app.core.config import settings
from app.core.logger import logger


class ChromaIngester:
    """Класс для загрузки данных в Chroma DB."""
    
    def __init__(self, chunks_path: Path = None, chroma_dir: Path = None):
        self.chunks_path = chunks_path or settings.chunks_dir / "moodle_chunks.jsonl"
        self.chroma_dir = chroma_dir or settings.chroma_dir
        
        # Инициализируем Chroma
        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        
        # Загружаем модель эмбеддингов
        logger.info(f"Загружаем модель эмбеддингов: {settings.embedding_model}")
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        
        # Получаем или создаем коллекцию
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"description": "Moodle documentation chunks"}
        )
    
    def load_chunks(self) -> List[Dict]:
        """Загружает чанки из JSONL файла."""
        chunks = []
        
        if not self.chunks_path.exists():
            raise FileNotFoundError(f"Файл {self.chunks_path} не найден")
        
        logger.info(f"Загружаем чанки из {self.chunks_path}")
        
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        
        logger.info(f"Загружено {len(chunks)} чанков")
        return chunks
    
    def prepare_batch(self, chunks: List[Dict], batch_size: int = 64) -> List[List[Dict]]:
        """Подготавливает батчи для обработки."""
        batches = []
        for i in range(0, len(chunks), batch_size):
            batches.append(chunks[i:i + batch_size])
        return batches
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Создает эмбеддинги для текстов."""
        embeddings = self.embedding_model.encode(
            texts, 
            batch_size=32, 
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def ingest_chunks(self, chunks: List[Dict]) -> None:
        """Загружает чанки в Chroma DB."""
        logger.info("Начинаем загрузку чанков в Chroma DB")
        
        # Проверяем, есть ли уже данные в коллекции
        count = self.collection.count()
        if count > 0:
            logger.warning(f"В коллекции уже есть {count} документов. Очищаем...")
            # Получаем все ID и удаляем их
            all_data = self.collection.get()
            if all_data["ids"]:
                self.collection.delete(ids=all_data["ids"])
        
        # Подготавливаем батчи
        batches = self.prepare_batch(chunks)
        
        total_ingested = 0
        
        for batch in tqdm(batches, desc="Загрузка батчей"):
            try:
                # Извлекаем данные из батча
                texts = [chunk["text"] for chunk in batch]
                ids = [chunk["chunk_id"] for chunk in batch]
                metadatas = [
                    {
                        "title": chunk["title"],
                        "url": chunk["url"],
                        "page_id": chunk["page_id"],
                        "chunk_index": chunk["chunk_index"],
                        "total_chunks": chunk["total_chunks"]
                    }
                    for chunk in batch
                ]
                
                # Создаем эмбеддинги
                embeddings = self.create_embeddings(texts)
                
                # Добавляем в коллекцию
                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
                
                total_ingested += len(batch)
                
            except Exception as e:
                logger.error(f"Ошибка при загрузке батча: {e}")
                continue
        
        # Сохраняем изменения (persist автоматически при использовании persist_directory)
        pass
        
        logger.info(f"Загружено {total_ingested} чанков в Chroma DB")
    
    def verify_ingestion(self) -> None:
        """Проверяет успешность загрузки."""
        count = self.collection.count()
        logger.info(f"В коллекции {settings.collection_name}: {count} документов")
        
        # Тестовый поиск
        try:
            results = self.collection.query(
                query_texts=["course creation"],
                n_results=1
            )
            logger.info("Тестовый поиск прошел успешно")
        except Exception as e:
            logger.error(f"Ошибка при тестовом поиске: {e}")
    
    def run(self) -> None:
        """Основной метод запуска."""
        logger.info("Начинаем загрузку в Chroma DB")
        
        try:
            chunks = self.load_chunks()
            self.ingest_chunks(chunks)
            self.verify_ingestion()
            
            logger.info("Загрузка в Chroma DB завершена успешно")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке в Chroma DB: {e}")
            raise


def main():
    """Точка входа."""
    ingester = ChromaIngester()
    ingester.run()


if __name__ == "__main__":
    main() 