from urllib import response

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_GPconnect():
    response = client.get("/gpconnnect/9690937286")
    assert response.status_code == 200
