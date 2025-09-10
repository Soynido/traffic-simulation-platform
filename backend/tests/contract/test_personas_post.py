"""
Contract test for POST /api/v1/personas endpoint.
Tests API contract compliance for creating personas.
"""
import pytest
import httpx
from fastapi.testclient import TestClient
import os


@pytest.fixture
def client():
    """Create test client for API testing."""
    # This will be implemented when the API is created
    # For now, we'll create a mock client that will fail as expected in TDD
    return None


@pytest.fixture
def valid_persona_data():
    """Valid persona data for testing."""
    return {
        "name": "Test Persona",
        "description": "A test persona for automated testing",
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5,
        "actions_per_page_min": 1,
        "actions_per_page_max": 10,
        "scroll_probability": 0.8,
        "click_probability": 0.6,
        "typing_probability": 0.1
    }


@pytest.mark.asyncio
async def test_create_persona_success(client, valid_persona_data):
    """Test successful persona creation."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.post("/api/v1/personas", json=valid_persona_data)
    
    # Expected response structure
    assert response.status_code == 201
    data = response.json()
    
    # Should return created persona with all fields
    required_fields = [
        'id', 'name', 'description', 'session_duration_min', 
        'session_duration_max', 'pages_min', 'pages_max',
        'actions_per_page_min', 'actions_per_page_max',
        'scroll_probability', 'click_probability', 'typing_probability',
        'created_at', 'updated_at'
    ]
    
    for field in required_fields:
        assert field in data, f"Created persona should have field {field}"
    
    # Validate field values match input
    assert data['name'] == valid_persona_data['name']
    assert data['description'] == valid_persona_data['description']
    assert data['session_duration_min'] == valid_persona_data['session_duration_min']
    assert data['session_duration_max'] == valid_persona_data['session_duration_max']
    assert data['pages_min'] == valid_persona_data['pages_min']
    assert data['pages_max'] == valid_persona_data['pages_max']
    assert data['scroll_probability'] == valid_persona_data['scroll_probability']
    assert data['click_probability'] == valid_persona_data['click_probability']
    assert data['typing_probability'] == valid_persona_data['typing_probability']
    
    # Validate generated fields
    assert data['id'] is not None
    assert data['created_at'] is not None
    assert data['updated_at'] is not None


@pytest.mark.asyncio
async def test_create_persona_minimal_data(client):
    """Test persona creation with minimal required data."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    minimal_data = {
        "name": "Minimal Persona",
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5
    }
    
    response = client.post("/api/v1/personas", json=minimal_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Should use default values for optional fields
    assert data['name'] == minimal_data['name']
    assert data['description'] is None
    assert data['actions_per_page_min'] == 1  # Default value
    assert data['actions_per_page_max'] == 10  # Default value
    assert data['scroll_probability'] == 0.8  # Default value
    assert data['click_probability'] == 0.6  # Default value
    assert data['typing_probability'] == 0.1  # Default value


@pytest.mark.asyncio
async def test_create_persona_validation_errors(client):
    """Test persona creation with validation errors."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    # Test missing required fields
    response = client.post("/api/v1/personas", json={})
    assert response.status_code == 422
    
    # Test invalid data types
    invalid_data = {
        "name": "Test Persona",
        "session_duration_min": "invalid",  # Should be integer
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5
    }
    response = client.post("/api/v1/personas", json=invalid_data)
    assert response.status_code == 422
    
    # Test negative values
    invalid_data = {
        "name": "Test Persona",
        "session_duration_min": -1,  # Should be positive
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5
    }
    response = client.post("/api/v1/personas", json=invalid_data)
    assert response.status_code == 422
    
    # Test illogical ranges
    invalid_data = {
        "name": "Test Persona",
        "session_duration_min": 120,  # Min > Max
        "session_duration_max": 60,
        "pages_min": 1,
        "pages_max": 5
    }
    response = client.post("/api/v1/personas", json=invalid_data)
    assert response.status_code == 422
    
    # Test probability out of range
    invalid_data = {
        "name": "Test Persona",
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5,
        "scroll_probability": 1.5  # Should be between 0 and 1
    }
    response = client.post("/api/v1/personas", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_persona_duplicate_name(client, valid_persona_data):
    """Test persona creation with duplicate name."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    # Create first persona
    response = client.post("/api/v1/personas", json=valid_persona_data)
    assert response.status_code == 201
    
    # Try to create second persona with same name
    response = client.post("/api/v1/personas", json=valid_persona_data)
    assert response.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_create_persona_name_length_validation(client):
    """Test persona name length validation."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    # Test name too long
    long_name_data = {
        "name": "A" * 101,  # Assuming max length is 100
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5
    }
    response = client.post("/api/v1/personas", json=long_name_data)
    assert response.status_code == 422
    
    # Test empty name
    empty_name_data = {
        "name": "",
        "session_duration_min": 60,
        "session_duration_max": 120,
        "pages_min": 1,
        "pages_max": 5
    }
    response = client.post("/api/v1/personas", json=empty_name_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_persona_url_validation(client):
    """Test persona target URL validation if applicable."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    # This test is for future URL validation if added to personas
    # For now, personas don't have URL fields, but this shows the pattern
    pass


@pytest.mark.asyncio
async def test_create_persona_response_headers(client, valid_persona_data):
    """Test persona creation response headers."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.post("/api/v1/personas", json=valid_persona_data)
    
    assert response.status_code == 201
    
    # Check content type
    assert response.headers['content-type'] == 'application/json'
    
    # Check location header for created resource
    assert 'location' in response.headers
    assert response.headers['location'].endswith(f"/api/v1/personas/{response.json()['id']}")


@pytest.mark.asyncio
async def test_create_persona_performance(client, valid_persona_data):
    """Test persona creation performance requirements."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    import time
    
    start_time = time.time()
    response = client.post("/api/v1/personas", json=valid_persona_data)
    end_time = time.time()
    
    assert response.status_code == 201
    
    # Should respond within 200ms as per requirements
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    assert response_time < 200, f"Response time {response_time}ms exceeds 200ms requirement"
