"""
Integration test for persona creation workflow.
Tests end-to-end persona management functionality.
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


@pytest.mark.asyncio
async def test_persona_creation_workflow(db_session):
    """Test complete persona creation workflow."""
    # Step 1: Create persona
    persona_data = {
        'name': 'Integration Test Persona',
        'description': 'A persona for integration testing',
        'session_duration_min': 60,
        'session_duration_max': 120,
        'pages_min': 1,
        'pages_max': 5,
        'actions_per_page_min': 1,
        'actions_per_page_max': 10,
        'scroll_probability': 0.8,
        'click_probability': 0.6,
        'typing_probability': 0.1
    }
    
    # Insert persona
    result = await db_session.execute(text("""
        INSERT INTO personas (name, description, session_duration_min, session_duration_max,
                            pages_min, pages_max, actions_per_page_min, actions_per_page_max,
                            scroll_probability, click_probability, typing_probability)
        VALUES (:name, :description, :session_duration_min, :session_duration_max,
                :pages_min, :pages_max, :actions_per_page_min, :actions_per_page_max,
                :scroll_probability, :click_probability, :typing_probability)
        RETURNING id
    """), persona_data)
    
    persona_id = result.fetchone()[0]
    await db_session.commit()
    
    # Step 2: Verify persona was created
    result = await db_session.execute(text("""
        SELECT * FROM personas WHERE id = :persona_id
    """), {"persona_id": persona_id})
    
    persona = result.fetchone()
    assert persona is not None
    assert persona[1] == persona_data['name']  # name field
    assert persona[2] == persona_data['description']  # description field
    assert persona[3] == persona_data['session_duration_min']  # session_duration_min field
    
    # Step 3: Update persona
    update_data = {
        'persona_id': persona_id,
        'new_name': 'Updated Integration Test Persona',
        'new_description': 'Updated description for integration testing'
    }
    
    await db_session.execute(text("""
        UPDATE personas 
        SET name = :new_name, description = :new_description, updated_at = now()
        WHERE id = :persona_id
    """), update_data)
    await db_session.commit()
    
    # Step 4: Verify update
    result = await db_session.execute(text("""
        SELECT name, description FROM personas WHERE id = :persona_id
    """), {"persona_id": persona_id})
    
    updated_persona = result.fetchone()
    assert updated_persona[0] == update_data['new_name']
    assert updated_persona[1] == update_data['new_description']
    
    # Step 5: Cleanup
    await db_session.execute(text("DELETE FROM personas WHERE id = :persona_id"), {"persona_id": persona_id})
    await db_session.commit()


@pytest.mark.asyncio
async def test_persona_validation_workflow(db_session):
    """Test persona validation workflow with invalid data."""
    # Test 1: Invalid probability values
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO personas (name, session_duration_min, session_duration_max,
                                pages_min, pages_max, scroll_probability)
            VALUES ('Invalid Persona', 60, 120, 1, 5, 1.5)
        """))
        await db_session.commit()
    
    # Test 2: Invalid duration range
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO personas (name, session_duration_min, session_duration_max,
                                pages_min, pages_max)
            VALUES ('Invalid Persona 2', 120, 60, 1, 5)
        """))
        await db_session.commit()
    
    # Test 3: Duplicate name
    # First create a valid persona
    await db_session.execute(text("""
        INSERT INTO personas (name, session_duration_min, session_duration_max,
                            pages_min, pages_max)
        VALUES ('Duplicate Test Persona', 60, 120, 1, 5)
    """))
    await db_session.commit()
    
    # Try to create another with same name
    with pytest.raises(Exception):  # Should raise unique constraint violation
        await db_session.execute(text("""
            INSERT INTO personas (name, session_duration_min, session_duration_max,
                                pages_min, pages_max)
            VALUES ('Duplicate Test Persona', 60, 120, 1, 5)
        """))
        await db_session.commit()
    
    # Cleanup
    await db_session.execute(text("DELETE FROM personas WHERE name = 'Duplicate Test Persona'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_persona_usage_in_campaigns(db_session):
    """Test persona usage in campaigns workflow."""
    # Step 1: Create persona
    await db_session.execute(text("""
        INSERT INTO personas (name, session_duration_min, session_duration_max,
                            pages_min, pages_max)
        VALUES ('Campaign Test Persona', 60, 120, 1, 5)
    """))
    await db_session.commit()
    
    # Get persona ID
    result = await db_session.execute(text("""
        SELECT id FROM personas WHERE name = 'Campaign Test Persona'
    """))
    persona_id = result.fetchone()[0]
    
    # Step 2: Create campaign using persona
    campaign_data = {
        'name': 'Test Campaign',
        'target_url': 'https://example.com',
        'total_sessions': 100,
        'concurrent_sessions': 10,
        'persona_id': persona_id
    }
    
    result = await db_session.execute(text("""
        INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
        VALUES (:name, :target_url, :total_sessions, :concurrent_sessions, :persona_id)
        RETURNING id
    """), campaign_data)
    
    campaign_id = result.fetchone()[0]
    await db_session.commit()
    
    # Step 3: Verify campaign was created with correct persona
    result = await db_session.execute(text("""
        SELECT c.name, c.persona_id, p.name as persona_name
        FROM campaigns c
        JOIN personas p ON c.persona_id = p.id
        WHERE c.id = :campaign_id
    """), {"campaign_id": campaign_id})
    
    campaign_info = result.fetchone()
    assert campaign_info is not None
    assert campaign_info[0] == campaign_data['name']
    assert campaign_info[1] == persona_id
    assert campaign_info[2] == 'Campaign Test Persona'
    
    # Step 4: Test foreign key constraint - cannot delete persona used in campaign
    with pytest.raises(Exception):  # Should raise foreign key constraint violation
        await db_session.execute(text("""
            DELETE FROM personas WHERE id = :persona_id
        """), {"persona_id": persona_id})
        await db_session.commit()
    
    # Step 5: Cleanup - delete campaign first, then persona
    await db_session.execute(text("DELETE FROM campaigns WHERE id = :campaign_id"), {"campaign_id": campaign_id})
    await db_session.execute(text("DELETE FROM personas WHERE id = :persona_id"), {"persona_id": persona_id})
    await db_session.commit()


@pytest.mark.asyncio
async def test_persona_listing_workflow(db_session):
    """Test persona listing and filtering workflow."""
    # Create multiple personas for testing
    personas = [
        ('Persona A', 60, 120, 1, 5),
        ('Persona B', 30, 90, 2, 8),
        ('Persona C', 120, 300, 3, 10)
    ]
    
    persona_ids = []
    for name, min_dur, max_dur, min_pages, max_pages in personas:
        result = await db_session.execute(text("""
            INSERT INTO personas (name, session_duration_min, session_duration_max,
                                pages_min, pages_max)
            VALUES (:name, :min_dur, :max_dur, :min_pages, :max_pages)
            RETURNING id
        """), {
            "name": name, "min_dur": min_dur, "max_dur": max_dur,
            "min_pages": min_pages, "max_pages": max_pages
        })
        persona_ids.append(result.fetchone()[0])
    
    await db_session.commit()
    
    # Test listing all personas
    result = await db_session.execute(text("""
        SELECT id, name, session_duration_min, session_duration_max
        FROM personas
        ORDER BY name
    """))
    
    all_personas = result.fetchall()
    assert len(all_personas) >= 3
    
    # Test filtering by duration range
    result = await db_session.execute(text("""
        SELECT id, name FROM personas
        WHERE session_duration_min >= 60 AND session_duration_max <= 150
        ORDER BY name
    """))
    
    filtered_personas = result.fetchall()
    assert len(filtered_personas) >= 1
    assert any(p[1] == 'Persona A' for p in filtered_personas)
    
    # Test searching by name
    result = await db_session.execute(text("""
        SELECT id, name FROM personas
        WHERE name LIKE '%Persona A%'
    """))
    
    search_results = result.fetchall()
    assert len(search_results) == 1
    assert search_results[0][1] == 'Persona A'
    
    # Cleanup
    for persona_id in persona_ids:
        await db_session.execute(text("DELETE FROM personas WHERE id = :persona_id"), {"persona_id": persona_id})
    await db_session.commit()
