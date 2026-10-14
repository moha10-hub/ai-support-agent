from fastapi.testclient import TestClient

from orders_api.main import app

client = TestClient(app)


def test_get_existing_order():
    response = client.get("/orders/1001")
    assert response.status_code == 200
    assert response.json()["status"] == "spedito"


def test_get_missing_order_returns_404():
    response = client.get("/orders/9999")
    assert response.status_code == 404