import pytest

from app import add, app, divide


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -1) == -2


def test_divide_normal():
    assert divide(10, 2) == 5


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        divide(10, 0)


def test_home_route_status_code(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_route_returns_healthy(client):
    response = client.get("/")
    data = response.get_json()
    assert data["status"] == "healthy"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    