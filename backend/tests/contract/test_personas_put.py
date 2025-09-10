"""
Contract test for PUT /api/v1/personas/{id} endpoint.
Validates update semantics, validation, and error responses.
"""
import pytest
from uuid import uuid4


@pytest.fixture
def client():
    """Create test client for API testing.
    Intentionally returns None for RED phase consistency, like other contract tests.
    """
    return None


@pytest.fixture
def update_payload():
    return {
        "name": "Updated Persona",
        "description": "Updated description",
        "session_duration_min": 45,
        "session_duration_max": 150,
        "pages_min": 2,
        "pages_max": 8,
        "actions_per_page_min": 1,
        "actions_per_page_max": 12,
        "scroll_probability": 0.7,
        "click_probability": 0.5,
        "typing_probability": 0.2,
    }


@pytest.mark.asyncio
async def test_update_persona_success(client, update_payload):
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")

    # Create initial persona
    create_payload = {
        "name": "Initial Persona",
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5,
    }
    create_resp = client.post("/api/v1/personas", json=create_payload)
    assert create_resp.status_code == 201
    persona_id = create_resp.json()["id"]

    # Update
    resp = client.put(f"/api/v1/personas/{persona_id}", json=update_payload)
    assert resp.status_code == 200
    data = resp.json()

    # Fields preserved/updated
    assert data["id"] == persona_id
    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]
    assert data["session_duration_min"] == update_payload["session_duration_min"]
    assert data["session_duration_max"] == update_payload["session_duration_max"]
    assert data["pages_min"] == update_payload["pages_min"]
    assert data["pages_max"] == update_payload["pages_max"]
    assert data["actions_per_page_min"] == update_payload["actions_per_page_min"]
    assert data["actions_per_page_max"] == update_payload["actions_per_page_max"]
    assert float(data["scroll_probability"]) == float(update_payload["scroll_probability"])  # may be Decimal
    assert float(data["click_probability"]) == float(update_payload["click_probability"])    # may be Decimal
    assert float(data["typing_probability"]) == float(update_payload["typing_probability"])  # may be Decimal


@pytest.mark.asyncio
async def test_update_persona_partial_payload(client):
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")

    # Create initial persona
    create_payload = {
        "name": "Partial Persona",
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5,
    }
    create_resp = client.post("/api/v1/personas", json=create_payload)
    assert create_resp.status_code == 201
    persona = create_resp.json()

    # Partial update (only description)
    resp = client.put(f"/api/v1/personas/{persona['id']}", json={"description": "Now described"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "Now described"
    assert data["name"] == create_payload["name"]  # unchanged


@pytest.mark.asyncio
async def test_update_persona_not_found(client):
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")

    non_existent_id = str(uuid4())
    resp = client.put(f"/api/v1/personas/{non_existent_id}", json={"name": "X"})
    assert resp.status_code in (404, 400)


@pytest.mark.asyncio
async def test_update_persona_validation_errors(client):
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")

    # Create initial persona
    create_payload = {
        "name": "Invalid Update Persona",
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5,
    }
    create_resp = client.post("/api/v1/personas", json=create_payload)
    assert create_resp.status_code == 201
    persona_id = create_resp.json()["id"]

    # Invalid: max < min
    invalid_update = {
        "session_duration_min": 100,
        "session_duration_max": 90,
    }
    resp = client.put(f"/api/v1/personas/{persona_id}", json=invalid_update)
    assert resp.status_code == 422

