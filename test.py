from fastapi.testclient import TestClient
from main import app  # ⚠️ Vérifie bien le chemin selon ton arborescence

client = TestClient(app)

def test_register_user():
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "cowboy",
        "profile_image": None
    }

    response = client.post("/auth/register", json=data)
    print("Réponse du serveur:", response.text)

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["username"] == "testuser"
    assert result["email"] == "test@example.com"
    assert result["role"] == "cowboy"
