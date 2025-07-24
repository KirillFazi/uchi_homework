#!/usr/bin/env python3
"""Скрипт для парсинга XML файлов экспорта в plain text."""
import sys
import pathlib

# Add project root to Python path
project_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import xml.etree.ElementTree as ET
from pathlib import Path
import json
import re

from app.core.config import settings
from app.core.logger import logger


def clean_wiki_text(text):
    """Очищает wiki markup из текста."""
    if not text:
        return ""
    
    # Убираем HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Убираем wiki ссылки [[текст|ссылка]] -> текст
    text = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    
    # Убираем внешние ссылки [url текст] -> текст
    text = re.sub(r'\[([^\s]+)\s+([^\]]+)\]', r'\2', text)
    text = re.sub(r'\[([^\s]+)\]', '', text)
    
    # Убираем заголовки === ===
    text = re.sub(r'={3,}([^=]+)={3,}', r'\n\1\n', text)
    text = re.sub(r'={2,}([^=]+)={2,}', r'\n\1\n', text)
    text = re.sub(r'=([^=]+)=', r'\n\1\n', text)
    
    # Убираем жирный и курсив
    text = re.sub(r"''''([^']+)''''", r'\1', text)
    text = re.sub(r"'''([^']+)'''", r'\1', text)
    text = re.sub(r"''([^']+)''", r'\1', text)
    
    # Убираем шаблоны {{template}}
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    
    # Убираем категории
    text = re.sub(r'\[\[Category:[^\]]+\]\]', '', text)
    
    # Убираем файлы
    text = re.sub(r'\[\[File:[^\]]+\]\]', '', text)
    text = re.sub(r'\[\[Image:[^\]]+\]\]', '', text)
    
    # Убираем таблицы (упрощенно)
    text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
    
    # Убираем лишние пробелы и переносы строк
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()
    
    return text


def parse_xml_file(xml_file):
    """Парсит один XML файл и извлекает страницы."""
    pages = []
    
    try:
        logger.info(f"Парсим файл: {xml_file}")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # MediaWiki XML использует namespace
        ns = {"mw": "http://www.mediawiki.org/xml/export-0.11/"}
        
        # Ищем все страницы
        for page in root.findall("mw:page", ns):
            try:
                title_elem = page.find("mw:title", ns)
                title = title_elem.text if title_elem is not None else ""
                
                if not title:
                    continue
                
                # Пропускаем служебные страницы
                if any(skip in title for skip in [
                    "Talk:", "User:", "Template:", "Help:", "Category:", 
                    "File:", "MediaWiki:", "Special:", "Module:"
                ]):
                    continue
                
                # Ищем последнюю ревизию
                rev = page.find("mw:revision", ns)
                if rev is None:
                    continue
                
                text_elem = rev.find("mw:text", ns)
                wiki_text = text_elem.text if text_elem is not None else ""
                
                # Очищаем wiki markup
                plain_text = clean_wiki_text(wiki_text)
                
                if len(plain_text.strip()) < 50:  # Пропускаем слишком короткие страницы
                    continue
                
                # Создаем запись
                page_data = {
                    "id": str(len(pages) + 1),
                    "title": title,
                    "text": plain_text[:5000],  # Ограничиваем длину
                    "url": f"https://docs.moodle.org/403/en/{title.replace(' ', '_')}",
                    "timestamp": "",
                    "length": len(plain_text)
                }
                
                pages.append(page_data)
                
            except Exception as e:
                logger.warning(f"Ошибка при обработке страницы в {xml_file}: {e}")
                continue
        
        logger.info(f"Извлечено {len(pages)} страниц из {xml_file}")
        
    except ET.ParseError as e:
        logger.error(f"Ошибка парсинга XML файла {xml_file}: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке {xml_file}: {e}")
    
    return pages


def main():
    """Основная функция."""
    xml_dir = settings.raw_dir / "xml"
    output_file = settings.raw_dir / "moodle_docs.jsonl"
    
    if not xml_dir.exists():
        logger.error(f"Папка с XML файлами не найдена: {xml_dir}")
        logger.info("Сначала запустите: python scripts/export_pages.py")
        return
    
    # Ищем XML файлы
    xml_files = sorted(xml_dir.glob("*.xml"))
    if not xml_files:
        logger.error(f"XML файлы не найдены в {xml_dir}")
        return
    
    logger.info(f"Найдено {len(xml_files)} XML файлов для обработки")
    
    # Обрабатываем все XML файлы
    all_pages = []
    
    for xml_file in xml_files:
        pages = parse_xml_file(xml_file)
        all_pages.extend(pages)
    
    if not all_pages:
        logger.error("Не удалось извлечь ни одной страницы")
        return
    
    # Переназначаем ID
    for i, page in enumerate(all_pages, 1):
        page["id"] = str(i)
    
    # Сохраняем в JSONL
    logger.info(f"Сохраняем {len(all_pages)} страниц в {output_file}")
    
    try:
        with output_file.open("w", encoding="utf-8") as out:
            for page in all_pages:
                out.write(json.dumps(page, ensure_ascii=False) + "\n")
        
        logger.info(f"Успешно сохранено {len(all_pages)} страниц в {output_file}")
        logger.info("Теперь можно запустить: python scripts/chunk_docs.py")
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла: {e}")


if __name__ == "__main__":
    main() 