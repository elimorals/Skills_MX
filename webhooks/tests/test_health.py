def test_health_ok(app_client):
    response = app_client.get("/webhooks/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["mode"] == "mock"
    assert data["version"]
