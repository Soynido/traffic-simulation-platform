"""
Contract test for page_visits table schema.
Tests database schema compliance for page_visit entity.
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
    """Create test data for page_visits tests."""
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
    
    await db_session.commit()
    
    # Get session ID
    session_result = await db_session.execute(text("""
        SELECT id FROM sessions WHERE start_url = 'https://example.com'
    """))
    session_id = session_result.fetchone()[0]
    
    yield {"session_id": session_id}
    
    # Cleanup
    await db_session.execute(text("DELETE FROM sessions WHERE start_url = 'https://example.com'"))
    await db_session.execute(text("DELETE FROM campaigns WHERE name = 'Test Campaign'"))
    await db_session.execute(text("DELETE FROM personas WHERE name = 'Test Persona'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_page_visits_table_exists(db_session):
    """Test that page_visits table exists with correct structure."""
    # Check table exists
    result = await db_session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'page_visits'
    """))
    assert result.fetchone() is not None, "page_visits table should exist"


@pytest.mark.asyncio
async def test_page_visits_table_columns(db_session):
    """Test that page_visits table has all required columns with correct types."""
    result = await db_session.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'page_visits'
        ORDER BY ordinal_position
    """))
    
    columns = {row[0]: {'type': row[1], 'nullable': row[2] == 'YES', 'default': row[3]} 
              for row in result.fetchall()}
    
    # Required columns
    expected_columns = {
        'id': {'type': 'uuid', 'nullable': False, 'default': True},
        'session_id': {'type': 'uuid', 'nullable': False, 'default': False},
        'url': {'type': 'character varying', 'nullable': False, 'default': False},
        'title': {'type': 'text', 'nullable': True, 'default': False},
        'visit_order': {'type': 'integer', 'nullable': False, 'default': False},
        'arrived_at': {'type': 'timestamp with time zone', 'nullable': False, 'default': False},
        'left_at': {'type': 'timestamp with time zone', 'nullable': True, 'default': False},
        'dwell_time_ms': {'type': 'integer', 'nullable': True, 'default': False},  # Generated column
        'actions_count': {'type': 'integer', 'nullable': False, 'default': True},
        'scroll_depth_percent': {'type': 'integer', 'nullable': False, 'default': True}
    }
    
    for col_name, expected in expected_columns.items():
        assert col_name in columns, f"Column {col_name} should exist"
        col = columns[col_name]
        assert col['type'] == expected['type'], f"Column {col_name} should have type {expected['type']}, got {col['type']}"
        assert col['nullable'] == expected['nullable'], f"Column {col_name} nullable should be {expected['nullable']}"
        if expected['default']:
            assert col['default'] is not None, f"Column {col_name} should have default value"


@pytest.mark.asyncio
async def test_page_visits_table_constraints(db_session):
    """Test that page_visits table has correct constraints."""
    # Test primary key
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'page_visits' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    assert result.fetchone() is not None, "page_visits table should have primary key"
    
    # Test foreign key to sessions
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'page_visits' 
        AND constraint_type = 'FOREIGN KEY'
    """))
    assert result.fetchone() is not None, "page_visits table should have foreign key to sessions"
    
    # Test check constraints
    result = await db_session.execute(text("""
        SELECT constraint_name, check_clause
        FROM information_schema.check_constraints 
        WHERE constraint_schema = 'public' 
        AND constraint_name LIKE '%page_visits%'
    """))
    check_constraints = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have constraints for positive values and logical ranges
    assert any('visit_order > 0' in clause for clause in check_constraints.values()), "Should have constraint for positive visit_order"
    assert any('scroll_depth_percent BETWEEN 0 AND 100' in clause for clause in check_constraints.values()), "Should have constraint for scroll depth range"
    
    # Test unique constraint on (session_id, visit_order)
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'page_visits' 
        AND constraint_type = 'UNIQUE'
    """))
    assert result.fetchone() is not None, "page_visits table should have unique constraint on (session_id, visit_order)"


@pytest.mark.asyncio
async def test_page_visits_table_indexes(db_session):
    """Test that page_visits table has required indexes."""
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public' AND tablename = 'page_visits'
    """))
    
    indexes = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have indexes for session_id, visit_order, and url
    assert any('session_id' in idx_def and 'visit_order' in idx_def for idx_def in indexes.values()), "Should have index on (session_id, visit_order)"
    assert any('url' in idx_def for idx_def in indexes.values()), "Should have index on url"


@pytest.mark.asyncio
async def test_page_visits_table_insert_validation(db_session, test_data):
    """Test that page_visits table validates data correctly."""
    # Test valid insert
    await db_session.execute(text("""
        INSERT INTO page_visits (session_id, url, visit_order, arrived_at)
        VALUES (:session_id, 'https://example.com/page1', 1, now())
    """), test_data)
    await db_session.commit()
    
    # Test invalid insert - negative visit_order
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO page_visits (session_id, url, visit_order, arrived_at)
            VALUES (:session_id, 'https://example.com/page2', -1, now())
        """), test_data)
        await db_session.commit()
    
    # Test invalid insert - scroll_depth_percent out of range
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO page_visits (session_id, url, visit_order, arrived_at, scroll_depth_percent)
            VALUES (:session_id, 'https://example.com/page3', 2, now(), 150)
        """), test_data)
        await db_session.commit()
    
    # Test invalid insert - duplicate (session_id, visit_order)
    with pytest.raises(Exception):  # Should raise unique constraint violation
        await db_session.execute(text("""
            INSERT INTO page_visits (session_id, url, visit_order, arrived_at)
            VALUES (:session_id, 'https://example.com/page4', 1, now())
        """), test_data)
        await db_session.commit()


@pytest.mark.asyncio
async def test_page_visits_table_foreign_key_constraint(db_session):
    """Test that page_visits table enforces foreign key to sessions."""
    # Test invalid insert - non-existent session_id
    with pytest.raises(Exception):  # Should raise foreign key constraint violation
        await db_session.execute(text("""
            INSERT INTO page_visits (session_id, url, visit_order, arrived_at)
            VALUES ('00000000-0000-0000-0000-000000000000', 'https://example.com', 1, now())
        """))
        await db_session.commit()


@pytest.mark.asyncio
async def test_page_visits_table_cascade_delete(db_session, test_data):
    """Test that page_visits are deleted when session is deleted (CASCADE)."""
    # Create a page visit
    await db_session.execute(text("""
        INSERT INTO page_visits (session_id, url, visit_order, arrived_at)
        VALUES (:session_id, 'https://example.com/page1', 1, now())
    """), test_data)
    await db_session.commit()
    
    # Verify page visit exists
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM page_visits WHERE session_id = :session_id
    """), test_data)
    assert result.fetchone()[0] == 1, "Page visit should exist"
    
    # Delete session (should cascade delete page visits)
    await db_session.execute(text("""
        DELETE FROM sessions WHERE id = :session_id
    """), test_data)
    await db_session.commit()
    
    # Verify page visit was deleted
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM page_visits WHERE session_id = :session_id
    """), test_data)
    assert result.fetchone()[0] == 0, "Page visit should be deleted when session is deleted"


@pytest.mark.asyncio
async def test_page_visits_table_cleanup(db_session):
    """Clean up test data."""
    await db_session.execute(text("DELETE FROM page_visits WHERE url LIKE 'https://example.com%'"))
    await db_session.commit()
