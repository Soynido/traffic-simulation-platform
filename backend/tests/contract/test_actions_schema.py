"""
Contract test for actions table schema.
Tests database schema compliance for action entity.
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
async def test_data(db_session):
    """Create test data for actions tests."""
    # Create test persona
    await db_session.execute(text("""
        INSERT INTO personas (name, session_duration_min, session_duration_max, pages_min, pages_max)
        VALUES ('Test Persona', 60, 120, 1, 5)
    """))
    
    # Create test campaign
    await db_session.execute(text("""
        INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
        VALUES ('Test Campaign', 'https://example.com', 100, 10, 
                (SELECT id FROM personas WHERE name = 'Test Persona'))
    """))
    
    # Create test session
    await db_session.execute(text("""
        INSERT INTO sessions (campaign_id, persona_id, start_url, user_agent)
        VALUES ((SELECT id FROM campaigns WHERE name = 'Test Campaign'),
                (SELECT id FROM personas WHERE name = 'Test Persona'),
                'https://example.com', 'Mozilla/5.0 Test Browser')
    """))
    
    # Create test page visit
    await db_session.execute(text("""
        INSERT INTO page_visits (session_id, url, visit_order, arrived_at)
        VALUES ((SELECT id FROM sessions WHERE start_url = 'https://example.com'),
                'https://example.com/page1', 1, now())
    """))
    
    await db_session.commit()
    
    # Get page visit ID
    page_visit_result = await db_session.execute(text("""
        SELECT id FROM page_visits WHERE url = 'https://example.com/page1'
    """))
    page_visit_id = page_visit_result.fetchone()[0]
    
    yield {"page_visit_id": page_visit_id}
    
    # Cleanup
    await db_session.execute(text("DELETE FROM page_visits WHERE url = 'https://example.com/page1'"))
    await db_session.execute(text("DELETE FROM sessions WHERE start_url = 'https://example.com'"))
    await db_session.execute(text("DELETE FROM campaigns WHERE name = 'Test Campaign'"))
    await db_session.execute(text("DELETE FROM personas WHERE name = 'Test Persona'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_actions_table_exists(db_session):
    """Test that actions table exists with correct structure."""
    # Check table exists
    result = await db_session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'actions'
    """))
    assert result.fetchone() is not None, "actions table should exist"


@pytest.mark.asyncio
async def test_actions_table_columns(db_session):
    """Test that actions table has all required columns with correct types."""
    result = await db_session.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'actions'
        ORDER BY ordinal_position
    """))
    
    columns = {row[0]: {'type': row[1], 'nullable': row[2] == 'YES', 'default': row[3]} 
              for row in result.fetchall()}
    
    # Required columns
    expected_columns = {
        'id': {'type': 'uuid', 'nullable': False, 'default': True},
        'page_visit_id': {'type': 'uuid', 'nullable': False, 'default': False},
        'action_type': {'type': 'USER-DEFINED', 'nullable': False, 'default': False},  # action_type enum
        'element_selector': {'type': 'text', 'nullable': True, 'default': False},
        'element_text': {'type': 'text', 'nullable': True, 'default': False},
        'coordinates_x': {'type': 'integer', 'nullable': True, 'default': False},
        'coordinates_y': {'type': 'integer', 'nullable': True, 'default': False},
        'input_value': {'type': 'text', 'nullable': True, 'default': False},
        'timestamp': {'type': 'timestamp with time zone', 'nullable': False, 'default': True},
        'action_order': {'type': 'integer', 'nullable': False, 'default': False},
        'duration_ms': {'type': 'integer', 'nullable': False, 'default': True}
    }
    
    for col_name, expected in expected_columns.items():
        assert col_name in columns, f"Column {col_name} should exist"
        col = columns[col_name]
        assert col['type'] == expected['type'], f"Column {col_name} should have type {expected['type']}, got {col['type']}"
        assert col['nullable'] == expected['nullable'], f"Column {col_name} nullable should be {expected['nullable']}"
        if expected['default']:
            assert col['default'] is not None, f"Column {col_name} should have default value"


@pytest.mark.asyncio
async def test_action_type_enum_exists(db_session):
    """Test that action_type enum type exists with correct values."""
    result = await db_session.execute(text("""
        SELECT enumlabel
        FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = 'action_type'
        ORDER BY e.enumsortorder
    """))
    
    enum_values = [row[0] for row in result.fetchall()]
    expected_values = [
        'click', 'double_click', 'right_click',
        'scroll', 'scroll_to_element',
        'type', 'clear', 'select',
        'hover', 'drag_and_drop',
        'key_press', 'page_load', 'page_unload'
    ]
    
    assert enum_values == expected_values, f"action_type enum should have values {expected_values}, got {enum_values}"


@pytest.mark.asyncio
async def test_actions_table_constraints(db_session):
    """Test that actions table has correct constraints."""
    # Test primary key
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'actions' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    assert result.fetchone() is not None, "actions table should have primary key"
    
    # Test foreign key to page_visits
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'actions' 
        AND constraint_type = 'FOREIGN KEY'
    """))
    assert result.fetchone() is not None, "actions table should have foreign key to page_visits"
    
    # Test check constraints
    result = await db_session.execute(text("""
        SELECT constraint_name, check_clause
        FROM information_schema.check_constraints 
        WHERE constraint_schema = 'public' 
        AND constraint_name LIKE '%actions%'
    """))
    check_constraints = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have constraint for positive action_order
    assert any('action_order > 0' in clause for clause in check_constraints.values()), "Should have constraint for positive action_order"
    
    # Test unique constraint on (page_visit_id, action_order)
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'actions' 
        AND constraint_type = 'UNIQUE'
    """))
    assert result.fetchone() is not None, "actions table should have unique constraint on (page_visit_id, action_order)"


@pytest.mark.asyncio
async def test_actions_table_indexes(db_session):
    """Test that actions table has required indexes."""
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public' AND tablename = 'actions'
    """))
    
    indexes = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have indexes for page_visit_id, action_order, action_type, and timestamp
    assert any('page_visit_id' in idx_def and 'action_order' in idx_def for idx_def in indexes.values()), "Should have index on (page_visit_id, action_order)"
    assert any('action_type' in idx_def and 'timestamp' in idx_def for idx_def in indexes.values()), "Should have index on (action_type, timestamp)"


@pytest.mark.asyncio
async def test_actions_table_insert_validation(db_session, test_data):
    """Test that actions table validates data correctly."""
    # Test valid insert
    await db_session.execute(text("""
        INSERT INTO actions (page_visit_id, action_type, action_order, timestamp)
        VALUES (:page_visit_id, 'click', 1, now())
    """), test_data)
    await db_session.commit()
    
    # Test invalid insert - negative action_order
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO actions (page_visit_id, action_type, action_order, timestamp)
            VALUES (:page_visit_id, 'click', -1, now())
        """), test_data)
        await db_session.commit()
    
    # Test invalid insert - invalid action_type
    with pytest.raises(Exception):  # Should raise enum constraint violation
        await db_session.execute(text("""
            INSERT INTO actions (page_visit_id, action_type, action_order, timestamp)
            VALUES (:page_visit_id, 'invalid_action', 2, now())
        """), test_data)
        await db_session.commit()
    
    # Test invalid insert - duplicate (page_visit_id, action_order)
    with pytest.raises(Exception):  # Should raise unique constraint violation
        await db_session.execute(text("""
            INSERT INTO actions (page_visit_id, action_type, action_order, timestamp)
            VALUES (:page_visit_id, 'scroll', 1, now())
        """), test_data)
        await db_session.commit()


@pytest.mark.asyncio
async def test_actions_table_foreign_key_constraint(db_session):
    """Test that actions table enforces foreign key to page_visits."""
    # Test invalid insert - non-existent page_visit_id
    with pytest.raises(Exception):  # Should raise foreign key constraint violation
        await db_session.execute(text("""
            INSERT INTO actions (page_visit_id, action_type, action_order, timestamp)
            VALUES ('00000000-0000-0000-0000-000000000000', 'click', 1, now())
        """))
        await db_session.commit()


@pytest.mark.asyncio
async def test_actions_table_cascade_delete(db_session, test_data):
    """Test that actions are deleted when page_visit is deleted (CASCADE)."""
    # Create an action
    await db_session.execute(text("""
        INSERT INTO actions (page_visit_id, action_type, action_order, timestamp)
        VALUES (:page_visit_id, 'click', 1, now())
    """), test_data)
    await db_session.commit()
    
    # Verify action exists
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM actions WHERE page_visit_id = :page_visit_id
    """), test_data)
    assert result.fetchone()[0] == 1, "Action should exist"
    
    # Delete page visit (should cascade delete actions)
    await db_session.execute(text("""
        DELETE FROM page_visits WHERE id = :page_visit_id
    """), test_data)
    await db_session.commit()
    
    # Verify action was deleted
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM actions WHERE page_visit_id = :page_visit_id
    """), test_data)
    assert result.fetchone()[0] == 0, "Action should be deleted when page visit is deleted"


@pytest.mark.asyncio
async def test_actions_table_cleanup(db_session):
    """Clean up test data."""
    await db_session.execute(text("DELETE FROM actions WHERE action_type = 'click'"))
    await db_session.commit()
