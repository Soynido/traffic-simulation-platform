"""
Integration test for campaign creation and execution workflow.
Tests end-to-end campaign management functionality.
"""
import pytest
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os


@pytest.fixture
async def db_engine():
    """Create test database engine."""
    database_url = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://traffic_user:traffic_pass@localhost:5432/traffic_test")
    engine = create_async_engine(database_url, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create test database session."""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_persona(db_session):
    """Create test persona for campaign tests."""
    await db_session.execute(text("""
        INSERT INTO personas (name, session_duration_min, session_duration_max,
                            pages_min, pages_max)
        VALUES ('Campaign Test Persona', 60, 120, 1, 5)
    """))
    await db_session.commit()
    
    result = await db_session.execute(text("""
        SELECT id FROM personas WHERE name = 'Campaign Test Persona'
    """))
    persona_id = result.fetchone()[0]
    yield persona_id
    
    # Cleanup
    await db_session.execute(text("DELETE FROM personas WHERE name = 'Campaign Test Persona'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_campaign_creation_workflow(db_session, test_persona):
    """Test complete campaign creation workflow."""
    # Step 1: Create campaign
    campaign_data = {
        'name': 'Integration Test Campaign',
        'description': 'A campaign for integration testing',
        'target_url': 'https://example.com',
        'total_sessions': 100,
        'concurrent_sessions': 10,
        'persona_id': test_persona,
        'rate_limit_delay_ms': 1000,
        'user_agent_rotation': True,
        'respect_robots_txt': True
    }
    
    result = await db_session.execute(text("""
        INSERT INTO campaigns (name, description, target_url, total_sessions,
                             concurrent_sessions, persona_id, rate_limit_delay_ms,
                             user_agent_rotation, respect_robots_txt)
        VALUES (:name, :description, :target_url, :total_sessions,
                :concurrent_sessions, :persona_id, :rate_limit_delay_ms,
                :user_agent_rotation, :respect_robots_txt)
        RETURNING id
    """), campaign_data)
    
    campaign_id = result.fetchone()[0]
    await db_session.commit()
    
    # Step 2: Verify campaign was created
    result = await db_session.execute(text("""
        SELECT * FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    campaign = result.fetchone()
    assert campaign is not None
    assert campaign[1] == campaign_data['name']  # name field
    assert campaign[2] == campaign_data['description']  # description field
    assert campaign[3] == campaign_data['target_url']  # target_url field
    assert campaign[4] == campaign_data['total_sessions']  # total_sessions field
    assert campaign[5] == campaign_data['concurrent_sessions']  # concurrent_sessions field
    assert campaign[7] == 'pending'  # status field (default)
    
    # Step 3: Update campaign
    update_data = {
        'campaign_id': campaign_id,
        'new_name': 'Updated Integration Test Campaign',
        'new_description': 'Updated description for integration testing'
    }
    
    await db_session.execute(text("""
        UPDATE campaigns 
        SET name = :new_name, description = :new_description, updated_at = now()
        WHERE id = :campaign_id
    """), update_data)
    await db_session.commit()
    
    # Step 4: Verify update
    result = await db_session.execute(text("""
        SELECT name, description FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    updated_campaign = result.fetchone()
    assert updated_campaign[0] == update_data['new_name']
    assert updated_campaign[1] == update_data['new_description']
    
    # Step 5: Cleanup
    await db_session.execute(text("DELETE FROM campaigns WHERE id = :campaign_id"), {"campaign_id": campaign_id})
    await db_session.commit()


@pytest.mark.asyncio
async def test_campaign_status_transitions(db_session, test_persona):
    """Test campaign status transition workflow."""
    # Create campaign
    result = await db_session.execute(text("""
        INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
        VALUES ('Status Test Campaign', 'https://example.com', 100, 10, :persona_id)
        RETURNING id
    """), {"persona_id": test_persona})
    
    campaign_id = result.fetchone()[0]
    await db_session.commit()
    
    # Step 1: Verify initial status is 'pending'
    result = await db_session.execute(text("""
        SELECT status FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    status = result.fetchone()[0]
    assert status == 'pending'
    
    # Step 2: Start campaign (pending -> running)
    await db_session.execute(text("""
        UPDATE campaigns 
        SET status = 'running', started_at = now(), updated_at = now()
        WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    await db_session.commit()
    
    result = await db_session.execute(text("""
        SELECT status, started_at FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    status, started_at = result.fetchone()
    assert status == 'running'
    assert started_at is not None
    
    # Step 3: Pause campaign (running -> paused)
    await db_session.execute(text("""
        UPDATE campaigns 
        SET status = 'paused', updated_at = now()
        WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    await db_session.commit()
    
    result = await db_session.execute(text("""
        SELECT status FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    status = result.fetchone()[0]
    assert status == 'paused'
    
    # Step 4: Resume campaign (paused -> running)
    await db_session.execute(text("""
        UPDATE campaigns 
        SET status = 'running', updated_at = now()
        WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    await db_session.commit()
    
    result = await db_session.execute(text("""
        SELECT status FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    status = result.fetchone()[0]
    assert status == 'running'
    
    # Step 5: Complete campaign (running -> completed)
    await db_session.execute(text("""
        UPDATE campaigns 
        SET status = 'completed', completed_at = now(), updated_at = now()
        WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    await db_session.commit()
    
    result = await db_session.execute(text("""
        SELECT status, completed_at FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    status, completed_at = result.fetchone()
    assert status == 'completed'
    assert completed_at is not None
    
    # Cleanup
    await db_session.execute(text("DELETE FROM campaigns WHERE id = :campaign_id"), {"campaign_id": campaign_id})
    await db_session.commit()


@pytest.mark.asyncio
async def test_campaign_validation_workflow(db_session, test_persona):
    """Test campaign validation workflow with invalid data."""
    # Test 1: Invalid session counts
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
            VALUES ('Invalid Campaign', 'https://example.com', 5, 10, :persona_id)
        """), {"persona_id": test_persona})
        await db_session.commit()
    
    # Test 2: Invalid rate limit delay
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, 
                                 persona_id, rate_limit_delay_ms)
            VALUES ('Invalid Campaign 2', 'https://example.com', 100, 10, :persona_id, 50)
        """), {"persona_id": test_persona})
        await db_session.commit()
    
    # Test 3: Invalid persona_id
    with pytest.raises(Exception):  # Should raise foreign key constraint violation
        await db_session.execute(text("""
            INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
            VALUES ('Invalid Campaign 3', 'https://example.com', 100, 10, '00000000-0000-0000-0000-000000000000')
        """))
        await db_session.commit()


@pytest.mark.asyncio
async def test_campaign_session_creation_workflow(db_session, test_persona):
    """Test campaign session creation workflow."""
    # Create campaign
    result = await db_session.execute(text("""
        INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
        VALUES ('Session Test Campaign', 'https://example.com', 5, 2, :persona_id)
        RETURNING id
    """), {"persona_id": test_persona})
    
    campaign_id = result.fetchone()[0]
    await db_session.commit()
    
    # Create sessions for the campaign
    session_data = [
        ('https://example.com/page1', 'Mozilla/5.0 Test Browser 1'),
        ('https://example.com/page2', 'Mozilla/5.0 Test Browser 2'),
        ('https://example.com/page3', 'Mozilla/5.0 Test Browser 3')
    ]
    
    session_ids = []
    for url, user_agent in session_data:
        result = await db_session.execute(text("""
            INSERT INTO sessions (campaign_id, persona_id, start_url, user_agent)
            VALUES (:campaign_id, :persona_id, :url, :user_agent)
            RETURNING id
        """), {
            "campaign_id": campaign_id,
            "persona_id": test_persona,
            "url": url,
            "user_agent": user_agent
        })
        session_ids.append(result.fetchone()[0])
    
    await db_session.commit()
    
    # Verify sessions were created
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM sessions WHERE campaign_id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    session_count = result.fetchone()[0]
    assert session_count == 3
    
    # Verify session details
    result = await db_session.execute(text("""
        SELECT s.start_url, s.user_agent, s.status, c.name as campaign_name
        FROM sessions s
        JOIN campaigns c ON s.campaign_id = c.id
        WHERE s.campaign_id = :campaign_id
        ORDER BY s.created_at
    """), {"campaign_id": campaign_id})
    
    sessions = result.fetchall()
    assert len(sessions) == 3
    
    for i, (url, user_agent, status, campaign_name) in enumerate(sessions):
        assert url == session_data[i][0]
        assert user_agent == session_data[i][1]
        assert status == 'pending'  # Default status
        assert campaign_name == 'Session Test Campaign'
    
    # Test cascade delete - deleting campaign should delete sessions
    await db_session.execute(text("DELETE FROM campaigns WHERE id = :campaign_id"), {"campaign_id": campaign_id})
    await db_session.commit()
    
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM sessions WHERE campaign_id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    session_count = result.fetchone()[0]
    assert session_count == 0  # Sessions should be deleted


@pytest.mark.asyncio
async def test_campaign_analytics_workflow(db_session, test_persona):
    """Test campaign analytics workflow."""
    # Create campaign
    result = await db_session.execute(text("""
        INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
        VALUES ('Analytics Test Campaign', 'https://example.com', 10, 2, :persona_id)
        RETURNING id
    """), {"persona_id": test_persona})
    
    campaign_id = result.fetchone()[0]
    await db_session.commit()
    
    # Create campaign analytics
    analytics_data = {
        'campaign_id': campaign_id,
        'total_sessions': 10,
        'completed_sessions': 8,
        'failed_sessions': 2,
        'success_rate': 0.8,
        'avg_session_duration_ms': 120000,
        'avg_pages_per_session': 3.5,
        'avg_actions_per_session': 15.2,
        'avg_rhythm_score': 0.75,
        'behavioral_variance': 0.12,
        'detection_risk_score': 0.25,
        'total_runtime_ms': 1200000,
        'avg_cpu_usage': 45.5,
        'peak_memory_mb': 512
    }
    
    await db_session.execute(text("""
        INSERT INTO campaign_analytics (campaign_id, total_sessions, completed_sessions,
                                      failed_sessions, success_rate, avg_session_duration_ms,
                                      avg_pages_per_session, avg_actions_per_session,
                                      avg_rhythm_score, behavioral_variance, detection_risk_score,
                                      total_runtime_ms, avg_cpu_usage, peak_memory_mb)
        VALUES (:campaign_id, :total_sessions, :completed_sessions, :failed_sessions,
                :success_rate, :avg_session_duration_ms, :avg_pages_per_session,
                :avg_actions_per_session, :avg_rhythm_score, :behavioral_variance,
                :detection_risk_score, :total_runtime_ms, :avg_cpu_usage, :peak_memory_mb)
    """), analytics_data)
    await db_session.commit()
    
    # Verify analytics were created
    result = await db_session.execute(text("""
        SELECT * FROM campaign_analytics WHERE campaign_id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    analytics = result.fetchone()
    assert analytics is not None
    assert analytics[1] == campaign_id  # campaign_id field
    assert analytics[2] == analytics_data['total_sessions']  # total_sessions field
    assert analytics[3] == analytics_data['completed_sessions']  # completed_sessions field
    assert analytics[4] == analytics_data['failed_sessions']  # failed_sessions field
    assert float(analytics[5]) == analytics_data['success_rate']  # success_rate field
    
    # Test analytics query with campaign details
    result = await db_session.execute(text("""
        SELECT c.name, c.target_url, ca.success_rate, ca.avg_session_duration_ms,
               ca.detection_risk_score
        FROM campaigns c
        JOIN campaign_analytics ca ON c.id = ca.campaign_id
        WHERE c.id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    campaign_analytics = result.fetchone()
    assert campaign_analytics is not None
    assert campaign_analytics[0] == 'Analytics Test Campaign'
    assert campaign_analytics[1] == 'https://example.com'
    assert float(campaign_analytics[2]) == 0.8
    assert campaign_analytics[3] == 120000
    assert float(campaign_analytics[4]) == 0.25
    
    # Cleanup
    await db_session.execute(text("DELETE FROM campaign_analytics WHERE campaign_id = :campaign_id"), {"campaign_id": campaign_id})
    await db_session.execute(text("DELETE FROM campaigns WHERE id = :campaign_id"), {"campaign_id": campaign_id})
    await db_session.commit()
