import pytest
from fastapi.testclient import TestClient
from chat_app.main import app


@pytest.fixture
def client(memory_db, mock_chat_manager):
    with TestClient(app) as client:
        yield client


def test_get(client):
    response = client.get("/")
    assert response.status_code == 200
    # TODO


def test_websocket_with_lifespan(client):
    client_id = "test_client"
    with client.websocket_connect(f"/ws?client_id={client_id}") as websocket:
        data = websocket.receive_text()
        assert data == "HISTORY_END"
