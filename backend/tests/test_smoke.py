from app import create_app


def test_health_endpoint() -> None:
    app = create_app("testing")
    client = app.test_client()

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "panchito"


def test_listings_requires_auth_when_oidc_enabled() -> None:
    app = create_app("testing")
    app.config["OIDC_ENABLED"] = True
    client = app.test_client()

    response = client.get("/api/v1/listings")

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login")
