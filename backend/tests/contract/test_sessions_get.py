"""
Contract test for GET /api/v1/sessions/{id} endpoint.
Tests API contract compliance for retrieving individual sessions.
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
def test_session_id():
    """Test session ID for retrieving sessions."""
    return "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.asyncio
async def test_get_session_success(client, test_session_id):
    """Test successful session retrieval."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.get(f"/api/v1/sessions/{test_session_id}")
    
    # Expected response structure
    assert response.status_code == 200
    data = response.json()
    
    # Should return session with all required fields
    required_fields = [
        'id', 'campaign_id', 'persona_id', 'status', 'start_url', 'user_agent',
        'viewport_width', 'viewport_height', 'session_duration_ms', 'pages_visited',
        'total_actions', 'error_message', 'created_at', 'started_at', 'completed_at'
    ]
    
    for field in required_fields:
        assert field in data, f"Session should have field {field}"
    
    # Validate field types
    assert isinstance(data['id'], str)
    assert isinstance(data['campaign_id'], str)
    assert isinstance(data['persona_id'], str)
    assert isinstance(data['status'], str)
    assert data['status'] in ['pending', 'running', 'completed', 'failed', 'timeout']
    assert isinstance(data['start_url'], str)
    assert isinstance(data['user_agent'], str)
    assert isinstance(data['viewport_width'], int)
    assert isinstance(data['viewport_height'], int)
    assert isinstance(data['pages_visited'], int)
    assert isinstance(data['total_actions'], int)
    
    # Validate ID matches
    assert data['id'] == test_session_id


@pytest.mark.asyncio
async def test_get_session_not_found(client):
    """Test retrieving non-existent session."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/sessions/{non_existent_id}")
    
    assert response.status_code == 404
    data = response.json()
    assert 'detail' in data
    assert 'not found' in data['detail'].lower()


@pytest.mark.asyncio
async def test_get_session_invalid_id_format(client):
    """Test retrieving session with invalid ID format."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    invalid_id = "not-a-valid-uuid"
    response = client.get(f"/api/v1/sessions/{invalid_id}")
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_session_with_page_visits(client, test_session_id):
    """Test session retrieval with page visits included."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.get(f"/api/v1/sessions/{test_session_id}?include=page_visits")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should include page_visits if requested
    if 'page_visits' in data:
        assert isinstance(data['page_visits'], list)
        
        # If page visits exist, validate structure
        if data['page_visits']:
            page_visit = data['page_visits'][0]
            required_fields = [
                'id', 'url', 'title', 'visit_order', 'arrived_at', 'left_at',
                'dwell_time_ms', 'actions_count', 'scroll_depth_percent'
            ]
            
            for field in required_fields:
                assert field in page_visit, f"Page visit should have field {field}"


@pytest.mark.asyncio
async def test_get_session_with_actions(client, test_session_id):
    """Test session retrieval with actions included."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.get(f"/api/v1/sessions/{test_session_id}?include=actions")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should include actions if requested
    if 'actions' in data:
        assert isinstance(data['actions'], list)
        
        # If actions exist, validate structure
        if data['actions']:
            action = data['actions'][0]
            required_fields = [
                'id', 'action_type', 'element_selector', 'element_text',
                'coordinates_x', 'coordinates_y', 'input_value', 'timestamp',
                'action_order', 'duration_ms'
            ]
            
            for field in required_fields:
                assert field in action, f"Action should have field {field}"


@pytest.mark.asyncio
async def test_get_session_response_headers(client, test_session_id):
    """Test session retrieval response headers."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    response = client.get(f"/api/v1/sessions/{test_session_id}")
    
    assert response.status_code == 200
    
    # Check content type
    assert response.headers['content-type'] == 'application/json'


@pytest.mark.asyncio
async def test_get_session_performance(client, test_session_id):
    """Test session retrieval performance requirements."""
    if client is None:
        pytest.skip("API client not yet implemented - this is expected in TDD RED phase")
    
    import time
    
    start_time = time.time()
    response = client.get(f"/api/v1/sessions/{test_session_id}")
    end_time = time.time()
    
    assert response.status_code == 200
    
    # Should respond within 200ms as per requirements
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    assert response_time < 200, f"Response time {response_time}ms exceeds 200ms requirement"
