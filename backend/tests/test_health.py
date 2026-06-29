def test_health_returns_200(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_body(client):
    response = client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert data["service"] == "jobpulse-backend"
    assert data["environment"] == "test"


def test_openapi_schema_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
