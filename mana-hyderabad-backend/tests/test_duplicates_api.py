from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import requires_database


client = TestClient(app)


@requires_database
def test_duplicate_suggestions_missing_complaint_returns_404():
    response = client.get("/api/admin/complaints/HYD-NOPE-9999/duplicate-suggestions")
    assert response.status_code == 404


@requires_database
def test_run_duplicate_check_missing_complaint_returns_404():
    response = client.post("/api/admin/complaints/HYD-NOPE-9999/run-duplicate-check")
    assert response.status_code == 404
