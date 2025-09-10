"""
Contract test for sessions table schema.
Tests database schema compliance for session entity.
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
    """Create test persona and campaign for session tests."""
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
    
    await db_session.commit()
    
    # Get IDs
    persona_result = await db_session.execute(text("SELECT id FROM personas WHERE name = 'Test Persona'"))
    campaign_result = await db_session.execute(text("SELECT id FROM campaigns WHERE name = 'Test Campaign'"))
    
    persona_id = persona_result.fetchone()[0]
    campaign_id = campaign_result.fetchone()[0]
    
    yield {"persona_id": persona_id, "campaign_id": campaign_id}
    
    # Cleanup
    await db_session.execute(text("DELETE FROM campaigns WHERE name = 'Test Campaign'"))
    await db_session.execute(text("DELETE FROM personas WHERE name = 'Test Persona'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_sessions_table_exists(db_session):
    """Test that sessions table exists with correct structure."""
    # Check table exists
    result = await db_session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'sessions'
    """))
    assert result.fetchone() is not None, "sessions table should exist"


@pytest.mark.asyncio
async def test_sessions_table_columns(db_session):
    """Test that sessions table has all required columns with correct types."""
    result = await db_session.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'sessions'
        ORDER BY ordinal_position
    """))
    
    columns = {row[0]: {'type': row[1], 'nullable': row[2] == 'YES', 'default': row[3]} 
              for row in result.fetchall()}
    
    # Required columns
    expected_columns = {
        'id': {'type': 'uuid', 'nullable': False, 'default': True},
        'campaign_id': {'type': 'uuid', 'nullable': False, 'default': False},
        'persona_id': {'type': 'uuid', 'nullable': False, 'default': False},
        'status': {'type': 'USER-DEFINED', 'nullable': False, 'default': True},  # session_status enum
        'start_url': {'type': 'character varying', 'nullable': False, 'default': False},
        'user_agent': {'type': 'text', 'nullable': False, 'default': False},
        'viewport_width': {'type': 'integer', 'nullable': False, 'default': True},
        'viewport_height': {'type': 'integer', 'nullable': False, 'default': True},
        'session_duration_ms': {'type': 'integer', 'nullable': True, 'default': False},
        'pages_visited': {'type': 'integer', 'nullable': False, 'default': True},
        'total_actions': {'type': 'integer', 'nullable': False, 'default': True},
        'error_message': {'type': 'text', 'nullable': True, 'default': False},
        'created_at': {'type': 'timestamp with time zone', 'nullable': False, 'default': True},
        'started_at': {'type': 'timestamp with time zone', 'nullable': True, 'default': False},
        'completed_at': {'type': 'timestamp with time zone', 'nullable': True, 'default': False}
    }
    
    for col_name, expected in expected_columns.items():
        assert col_name in columns, f"Column {col_name} should exist"
        col = columns[col_name]
        assert col['type'] == expected['type'], f"Column {col_name} should have type {expected['type']}, got {col['type']}"
        assert col['nullable'] == expected['nullable'], f"Column {col_name} nullable should be {expected['nullable']}"
        if expected['default']:
            assert col['default'] is not None, f"Column {col_name} should have default value"


@pytest.mark.asyncio
async def test_session_status_enum_exists(db_session):
    """Test that session_status enum type exists with correct values."""
    result = await db_session.execute(text("""
        SELECT enumlabel
        FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = 'session_status'
        ORDER BY e.enumsortorder
    """))
    
    enum_values = [row[0] for row in result.fetchall()]
    expected_values = ['pending', 'running', 'completed', 'failed', 'timeout']
    
    assert enum_values == expected_values, f"session_status enum should have values {expected_values}, got {enum_values}"


@pytest.mark.asyncio
async def test_sessions_table_constraints(db_session):
    """Test that sessions table has correct constraints."""
    # Test primary key
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'sessions' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    assert result.fetchone() is not None, "sessions table should have primary key"
    
    # Test foreign keys
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'sessions' 
        AND constraint_type = 'FOREIGN KEY'
    """))
    foreign_keys = result.fetchall()
    assert len(foreign_keys) >= 2, "sessions table should have foreign keys to campaigns and personas"


@pytest.mark.asyncio
async def test_sessions_table_indexes(db_session):
    """Test that sessions table has required indexes."""
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public' AND tablename = 'sessions'
    """))
    
    indexes = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have indexes for campaign_id, status, and created_at
    assert any('campaign_id' in idx_def and 'status' in idx_def for idx_def in indexes.values()), "Should have index on (campaign_id, status)"
    assert any('created_at' in idx_def for idx_def in indexes.values()), "Should have index on created_at"


@pytest.mark.asyncio
async def test_sessions_table_insert_validation(db_session, test_data):
    """Test that sessions table validates data correctly."""
    # Test valid insert
    await db_session.execute(text("""
        INSERT INTO sessions (campaign_id, persona_id, start_url, user_agent)
        VALUES (:campaign_id, :persona_id, 'https://example.com', 'Mozilla/5.0 Test Browser')
    """), test_data)
    await db_session.commit()
    
    # Test invalid insert - non-existent campaign_id
    with pytest.raises(Exception):  # Should raise foreign key constraint violation
        await db_session.execute(text("""
            INSERT INTO sessions (campaign_id, persona_id, start_url, user_agent)
            VALUES ('00000000-0000-0000-0000-000000000000', :persona_id, 'https://example.com', 'Mozilla/5.0 Test Browser')
        """), {"persona_id": test_data["persona_id"]})
        await db_session.commit()
    
    # Test invalid insert - non-existent persona_id
    with pytest.raises(Exception):  # Should raise foreign key constraint violation
        await db_session.execute(text("""
            INSERT INTO sessions (campaign_id, persona_id, start_url, user_agent)
            VALUES (:campaign_id, '00000000-0000-0000-0000-000000000000', 'https://example.com', 'Mozilla/5.0 Test Browser')
        """), {"campaign_id": test_data["campaign_id"]})
        await db_session.commit()


@pytest.mark.asyncio
async def test_sessions_table_cascade_delete(db_session, test_data):
    """Test that sessions are deleted when campaign is deleted (CASCADE)."""
    # Create a session
    await db_session.execute(text("""
        INSERT INTO sessions (campaign_id, persona_id, start_url, user_agent)
        VALUES (:campaign_id, :persona_id, 'https://example.com', 'Mozilla/5.0 Test Browser')
    """), test_data)
    await db_session.commit()
    
    # Verify session exists
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM sessions WHERE campaign_id = :campaign_id
    """), {"campaign_id": test_data["campaign_id"]})
    assert result.fetchone()[0] == 1, "Session should exist"
    
    # Delete campaign (should cascade delete session)
    await db_session.execute(text("""
        DELETE FROM campaigns WHERE id = :campaign_id
    """), {"campaign_id": test_data["campaign_id"]})
    await db_session.commit()
    
    # Verify session was deleted
    result = await db_session.execute(text("""
        SELECT COUNT(*) FROM sessions WHERE campaign_id = :campaign_id
    """), {"campaign_id": test_data["campaign_id"]})
    assert result.fetchone()[0] == 0, "Session should be deleted when campaign is deleted"


@pytest.mark.asyncio
async def test_sessions_table_cleanup(db_session):
    """Clean up test data."""
    await db_session.execute(text("DELETE FROM sessions WHERE start_url = 'https://example.com'"))
    await db_session.commit()
