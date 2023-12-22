import pytest
from fastapi.testclient import TestClient
from backend.src.main.main import app

client = TestClient(app)


@pytest.mark.parametrize("numbers",[(1,2,3,4,5),(3,3)])
def test_model_predict(numbers):
    response = client.post("/model_predict", json={"n": numbers})
    assert response.status_code == 200
    assert response.json() == {"average": 3.0}


