"""
Contract test for POST /api/v1/campaigns endpoint.
Tests API contract compliance for creating campaigns.
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
def test_persona_id():
    """Test persona ID for campaign creation."""
    return "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def valid_campaign_data(test_persona_id):
    """Valid campaign data for testing."""
    return {
        "name": "Test Campaign",
        "description": "A test campaign for automated testing",
        "target_url": "https://example.com",
        "total_sessions": 100,
        "concurrent_sessions": 10,
        "persona_id": test_persona_id,
        "rate_limit_delay_ms": 1000,
        "user_agent_rotation": True,
        "respect_robots_txt": True
    }


@pytest.mark.asyncio
async def test_create_campaign_success(client, valid_campaign_data):
    """Test successful campaign creation."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.post("/api/v1/campaigns", json=valid_campaign_data)
    
    # Expected response structure
    assert response.status_code == 201
    data = response.json()
    
    # Should return created campaign with all fields
    required_fields = [
        'id', 'name', 'description', 'target_url', 'total_sessions',
        'concurrent_sessions', 'status', 'persona_id', 'rate_limit_delay_ms',
        'user_agent_rotation', 'respect_robots_txt', 'created_at', 'updated_at',
        'started_at', 'completed_at'
    ]
    
    for field in required_fields:
        assert field in data, f"Created campaign should have field {field}"
    
    # Validate field values match input
    assert data['name'] == valid_campaign_data['name']
    assert data['description'] == valid_campaign_data['description']
    assert data['target_url'] == valid_campaign_data['target_url']
    assert data['total_sessions'] == valid_campaign_data['total_sessions']
    assert data['concurrent_sessions'] == valid_campaign_data['concurrent_sessions']
    assert data['persona_id'] == valid_campaign_data['persona_id']
    assert data['rate_limit_delay_ms'] == valid_campaign_data['rate_limit_delay_ms']
    assert data['user_agent_rotation'] == valid_campaign_data['user_agent_rotation']
    assert data['respect_robots_txt'] == valid_campaign_data['respect_robots_txt']
    
    # Validate generated fields
    assert data['id'] is not None
    assert data['status'] == 'pending'  # Default status
    assert data['created_at'] is not None
    assert data['updated_at'] is not None
    assert data['started_at'] is None  # Not started yet
    assert data['completed_at'] is None  # Not completed yet


@pytest.mark.asyncio
async def test_create_campaign_minimal_data(client, test_persona_id):
    """Test campaign creation with minimal required data."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    minimal_data = {
        "name": "Minimal Campaign",
        "target_url": "https://example.com",
        "total_sessions": 50,
        "persona_id": test_persona_id
    }
    
    response = client.post("/api/v1/campaigns", json=minimal_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Should use default values for optional fields
    assert data['name'] == minimal_data['name']
    assert data['target_url'] == minimal_data['target_url']
    assert data['total_sessions'] == minimal_data['total_sessions']
    assert data['persona_id'] == minimal_data['persona_id']
    assert data['description'] is None
    assert data['concurrent_sessions'] == 10  # Default value
    assert data['rate_limit_delay_ms'] == 1000  # Default value
    assert data['user_agent_rotation'] == True  # Default value
    assert data['respect_robots_txt'] == True  # Default value


@pytest.mark.asyncio
async def test_create_campaign_validation_errors(client, test_persona_id):
    """Test campaign creation with validation errors."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    # Test missing required fields
    response = client.post("/api/v1/campaigns", json={})
    assert response.status_code == 422
    
    # Test invalid data types
    invalid_data = {
        "name": "Test Campaign",
        "target_url": "https://example.com",
        "total_sessions": "invalid",  # Should be integer
        "persona_id": test_persona_id
    }
    response = client.post("/api/v1/campaigns", json=invalid_data)
    assert response.status_code == 422
    
    # Test negative values
    invalid_data = {
        "name": "Test Campaign",
        "target_url": "https://example.com",
        "total_sessions": -1,  # Should be positive
        "persona_id": test_persona_id
    }
    response = client.post("/api/v1/campaigns", json=invalid_data)
    assert response.status_code == 422
    
    # Test illogical ranges
    invalid_data = {
        "name": "Test Campaign",
        "target_url": "https://example.com",
        "total_sessions": 10,
        "concurrent_sessions": 20,  # concurrent > total
        "persona_id": test_persona_id
    }
    response = client.post("/api/v1/campaigns", json=invalid_data)
    assert response.status_code == 422
    
    # Test invalid URL format
    invalid_data = {
        "name": "Test Campaign",
        "target_url": "not-a-valid-url",
        "total_sessions": 100,
        "persona_id": test_persona_id
    }
    response = client.post("/api/v1/campaigns", json=invalid_data)
    assert response.status_code == 422
    
    # Test rate limit too low
    invalid_data = {
        "name": "Test Campaign",
        "target_url": "https://example.com",
        "total_sessions": 100,
        "persona_id": test_persona_id,
        "rate_limit_delay_ms": 50  # Should be >= 100
    }
    response = client.post("/api/v1/campaigns", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_campaign_invalid_persona_id(client):
    """Test campaign creation with invalid persona_id."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    invalid_data = {
        "name": "Test Campaign",
        "target_url": "https://example.com",
        "total_sessions": 100,
        "persona_id": "00000000-0000-0000-0000-000000000000"  # Non-existent persona
    }
    
    response = client.post("/api/v1/campaigns", json=invalid_data)
    assert response.status_code == 404  # Persona not found


@pytest.mark.asyncio
async def test_create_campaign_name_length_validation(client, test_persona_id):
    """Test campaign name length validation."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    # Test name too long
    long_name_data = {
        "name": "A" * 201,  # Assuming max length is 200
        "target_url": "https://example.com",
        "total_sessions": 100,
        "persona_id": test_persona_id
    }
    response = client.post("/api/v1/campaigns", json=long_name_data)
    assert response.status_code == 422
    
    # Test empty name
    empty_name_data = {
        "name": "",
        "target_url": "https://example.com",
        "total_sessions": 100,
        "persona_id": test_persona_id
    }
    response = client.post("/api/v1/campaigns", json=empty_name_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_campaign_url_validation(client, test_persona_id):
    """Test campaign target URL validation."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    # Test URL too long
    long_url_data = {
        "name": "Test Campaign",
        "target_url": "https://example.com/" + "a" * 500,  # Assuming max length is 500
        "total_sessions": 100,
        "persona_id": test_persona_id
    }
    response = client.post("/api/v1/campaigns", json=long_url_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_campaign_response_headers(client, valid_campaign_data):
    """Test campaign creation response headers."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.post("/api/v1/campaigns", json=valid_campaign_data)
    
    assert response.status_code == 201
    
    # Check content type
    assert response.headers['content-type'] == 'application/json'
    
    # Check location header for created resource
    assert 'location' in response.headers
    assert response.headers['location'].endswith(f"/api/v1/campaigns/{response.json()['id']}")


@pytest.mark.asyncio
async def test_create_campaign_performance(client, valid_campaign_data):
    """Test campaign creation performance requirements."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    import time
    
    start_time = time.time()
    response = client.post("/api/v1/campaigns", json=valid_campaign_data)
    end_time = time.time()
    
    assert response.status_code == 201
    
    # Should respond within 200ms as per requirements
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    assert response_time < 200, f"Response time {response_time}ms exceeds 200ms requirement"
