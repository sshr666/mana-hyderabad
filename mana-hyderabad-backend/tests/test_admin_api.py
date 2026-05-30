from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_admin_validation_rejects_invalid_pagination():
    response = client.get("/api/admin/complaints?page=0")
    assert response.status_code == 422


def test_admin_route_shapes_are_registered():
    paths = {route.path for route in app.routes}
    assert "/api/admin/complaints" in paths
    assert "/api/admin/map-points" in paths
    assert "/api/admin/nearby-complaints" in paths
    assert "/api/admin/hotspots" in paths
    assert "/api/admin/analytics" in paths
