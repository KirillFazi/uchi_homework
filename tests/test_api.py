"""Тесты для API."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Тест корневого эндпоинта."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_health_check():
    """Тест health check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "message" in data


def test_chat_endpoint():
    """Тест чат эндпоинта."""
    request_data = {
        "session_id": "test_session",
        "message": "Как создать курс в Moodle?"
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "session_id" in data
    assert data["session_id"] == "test_session"





def test_invalid_chat_request():
    """Тест некорректного запроса чата."""
    # Отсутствует обязательное поле
    request_data = {
        "session_id": "test_session"
        # отсутствует message
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    assert response.status_code == 422  # Validation error


def test_chat_with_empty_message():
    """Тест чата с пустым сообщением."""
    request_data = {
        "session_id": "test_session",
        "message": ""
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    assert response.status_code == 200  # Должен обработать пустое сообщение 