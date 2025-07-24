"""Управление памятью диалогов."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from app.core.logger import logger


class ConversationMemory:
    """Управление памятью диалогов."""
    
    def __init__(self, max_history_length: int = 10, session_timeout_hours: int = 24):
        self.memory: Dict[str, List[Dict]] = {}
        self.max_history_length = max_history_length
        self.session_timeout_hours = session_timeout_hours
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Добавляет сообщение в историю сессии."""
        if session_id not in self.memory:
            self.memory[session_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory[session_id].append(message)
        
        # Ограничиваем длину истории
        if len(self.memory[session_id]) > self.max_history_length * 2:
            self.memory[session_id] = self.memory[session_id][-self.max_history_length:]
        
        logger.debug(f"Добавлено сообщение в сессию {session_id}")
    
    def get_history(self, session_id: str, max_messages: int = 5) -> str:
        """Получает историю диалога в текстовом формате."""
        if session_id not in self.memory:
            return ""
        
        messages = self.memory[session_id][-max_messages:]
        
        history_parts = []
        for msg in messages:
            role = "Пользователь" if msg["role"] == "user" else "Ассистент"
            content = msg["content"]
            history_parts.append(f"{role}: {content}")
        
        return "\n".join(history_parts)
    
    def clear_session(self, session_id: str) -> bool:
        """Очищает историю сессии."""
        if session_id in self.memory:
            del self.memory[session_id]
            logger.info(f"Очищена сессия {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Очищает истекшие сессии."""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, messages in self.memory.items():
            if not messages:
                expired_sessions.append(session_id)
                continue
            
            # Проверяем время последнего сообщения
            last_message_time = datetime.fromisoformat(messages[-1]["timestamp"])
            if now - last_message_time > timedelta(hours=self.session_timeout_hours):
                expired_sessions.append(session_id)
        
        # Удаляем истекшие сессии
        for session_id in expired_sessions:
            del self.memory[session_id]
        
        if expired_sessions:
            logger.info(f"Очищено {len(expired_sessions)} истекших сессий")
        
        return len(expired_sessions)
    
    def get_stats(self) -> Dict:
        """Получает статистику памяти."""
        total_sessions = len(self.memory)
        total_messages = sum(len(messages) for messages in self.memory.values())
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "max_history_length": self.max_history_length,
            "session_timeout_hours": self.session_timeout_hours
        } 