#!/usr/bin/env python3
"""Скрипт для разбиения документов на чанки."""
import sys
import pathlib

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import re
from pathlib import Path
from typing import List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

from app.core.config import settings
from app.core.logger import logger


class DocumentChunker:
    """Класс для разбиения документов на чанки."""
    
    def __init__(self, input_path: Path = None, output_path: Path = None):
        self.input_path = input_path or settings.raw_dir / "moodle_docs.jsonl"
        self.output_path = output_path or settings.chunks_dir / "moodle_chunks.jsonl"
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def clean_text(self, text: str) -> str:
        """Очищает текст от мусора."""
        if not text:
            return ""
        
        # Убираем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Убираем повторяющиеся секции
        text = re.sub(r'See also.*?(?=\n\n|\n[A-Z]|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'References.*?(?=\n\n|\n[A-Z]|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Убираем HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        
        # Убираем вики-разметку
        text = re.sub(r'\[\[([^|\]]*?)\]\]', r'\1', text)  # [[link]] -> link
        text = re.sub(r'\[\[([^|]*?)\|([^\]]*?)\]\]', r'\2', text)  # [[link|text]] -> text
        text = re.sub(r'\{\{[^}]*\}\}', '', text)  # {{templates}}
        text = re.sub(r'==+([^=]+)==+', r'\1', text)  # ==headers==
        
        # Убираем лишние символы
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]]', '', text)
        
        return text.strip()
    
    def load_documents(self) -> List[Dict]:
        """Загружает документы из JSONL."""
        documents = []
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"Файл {self.input_path} не найден")
        
        logger.info(f"Загружаем документы из {self.input_path}")
        
        with open(self.input_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    documents.append(json.loads(line))
        
        logger.info(f"Загружено {len(documents)} документов")
        return documents
    
    def create_chunks(self, documents: List[Dict]) -> List[Dict]:
        """Создает чанки из документов."""
        chunks = []
        chunk_id = 0
        
        logger.info("Создаем чанки из документов")
        
        for doc in tqdm(documents, desc="Обработка документов"):
            # Очищаем текст
            clean_text = self.clean_text(doc.get("text", ""))
            
            if len(clean_text) < 50:  # Пропускаем слишком короткие документы
                continue
            
            # Разбиваем на чанки
            text_chunks = self.text_splitter.split_text(clean_text)
            
            for i, chunk_text in enumerate(text_chunks):
                if len(chunk_text.strip()) < 50:  # Пропускаем слишком короткие чанки
                    continue
                
                chunk = {
                    "chunk_id": f"{doc['id']}_{i}",
                    "page_id": doc["id"],
                    "title": doc["title"],
                    "url": doc["url"],
                    "text": chunk_text.strip(),
                    "chunk_index": i,
                    "total_chunks": len(text_chunks)
                }
                chunks.append(chunk)
                chunk_id += 1
        
        logger.info(f"Создано {len(chunks)} чанков")
        return chunks
    
    def save_chunks(self, chunks: List[Dict]) -> None:
        """Сохраняет чанки в JSONL файл."""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Сохраняем {len(chunks)} чанков в {self.output_path}")
        
        with open(self.output_path, "w", encoding="utf-8") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        
        logger.info(f"Чанки сохранены в {self.output_path}")
    
    def run(self) -> None:
        """Основной метод запуска."""
        logger.info("Начинаем разбиение документов на чанки")
        
        try:
            documents = self.load_documents()
            chunks = self.create_chunks(documents)
            self.save_chunks(chunks)
            
            logger.info("Разбиение на чанки завершено успешно")
            
        except Exception as e:
            logger.error(f"Ошибка при разбиении на чанки: {e}")
            raise


def main():
    """Точка входа."""
    chunker = DocumentChunker()
    chunker.run()


if __name__ == "__main__":
    main() 