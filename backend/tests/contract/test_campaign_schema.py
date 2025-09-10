"""
Contract test for campaigns table schema.
Tests database schema compliance for campaign entity.
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
        INSERT INTO personas (name, session_duration_min, session_duration_max, pages_min, pages_max)
        VALUES ('Test Persona', 60, 120, 1, 5)
    """))
    await db_session.commit()
    
    result = await db_session.execute(text("SELECT id FROM personas WHERE name = 'Test Persona'"))
    persona_id = result.fetchone()[0]
    yield persona_id
    
    # Cleanup
    await db_session.execute(text("DELETE FROM personas WHERE name = 'Test Persona'"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_campaigns_table_exists(db_session):
    """Test that campaigns table exists with correct structure."""
    # Check table exists
    result = await db_session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'campaigns'
    """))
    assert result.fetchone() is not None, "campaigns table should exist"


@pytest.mark.asyncio
async def test_campaigns_table_columns(db_session):
    """Test that campaigns table has all required columns with correct types."""
    result = await db_session.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'campaigns'
        ORDER BY ordinal_position
    """))
    
    columns = {row[0]: {'type': row[1], 'nullable': row[2] == 'YES', 'default': row[3]} 
              for row in result.fetchall()}
    
    # Required columns
    expected_columns = {
        'id': {'type': 'uuid', 'nullable': False, 'default': True},
        'name': {'type': 'character varying', 'nullable': False, 'default': False},
        'description': {'type': 'text', 'nullable': True, 'default': False},
        'target_url': {'type': 'character varying', 'nullable': False, 'default': False},
        'total_sessions': {'type': 'integer', 'nullable': False, 'default': False},
        'concurrent_sessions': {'type': 'integer', 'nullable': False, 'default': True},
        'status': {'type': 'USER-DEFINED', 'nullable': False, 'default': True},  # campaign_status enum
        'persona_id': {'type': 'uuid', 'nullable': False, 'default': False},
        'rate_limit_delay_ms': {'type': 'integer', 'nullable': False, 'default': True},
        'user_agent_rotation': {'type': 'boolean', 'nullable': False, 'default': True},
        'respect_robots_txt': {'type': 'boolean', 'nullable': False, 'default': True},
        'created_at': {'type': 'timestamp with time zone', 'nullable': False, 'default': True},
        'updated_at': {'type': 'timestamp with time zone', 'nullable': False, 'default': True},
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
async def test_campaign_status_enum_exists(db_session):
    """Test that campaign_status enum type exists with correct values."""
    result = await db_session.execute(text("""
        SELECT enumlabel
        FROM pg_enum e
        JOIN pg_type t ON e.enumtypid = t.oid
        WHERE t.typname = 'campaign_status'
        ORDER BY e.enumsortorder
    """))
    
    enum_values = [row[0] for row in result.fetchall()]
    expected_values = ['pending', 'running', 'paused', 'completed', 'failed']
    
    assert enum_values == expected_values, f"campaign_status enum should have values {expected_values}, got {enum_values}"


@pytest.mark.asyncio
async def test_campaigns_table_constraints(db_session):
    """Test that campaigns table has correct constraints."""
    # Test primary key
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'campaigns' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    assert result.fetchone() is not None, "campaigns table should have primary key"
    
    # Test foreign key to personas
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'campaigns' 
        AND constraint_type = 'FOREIGN KEY'
    """))
    assert result.fetchone() is not None, "campaigns table should have foreign key to personas"
    
    # Test check constraints
    result = await db_session.execute(text("""
        SELECT constraint_name, check_clause
        FROM information_schema.check_constraints 
        WHERE constraint_schema = 'public' 
        AND constraint_name LIKE '%campaigns%'
    """))
    check_constraints = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have constraints for positive values and logical ranges
    assert any('total_sessions > 0' in clause for clause in check_constraints.values()), "Should have constraint for positive total_sessions"
    assert any('concurrent_sessions > 0' in clause for clause in check_constraints.values()), "Should have constraint for positive concurrent_sessions"
    assert any('concurrent_sessions <= total_sessions' in clause for clause in check_constraints.values()), "Should have constraint for logical session count"
    assert any('rate_limit_delay_ms >= 100' in clause for clause in check_constraints.values()), "Should have constraint for minimum rate limit delay"


@pytest.mark.asyncio
async def test_campaigns_table_insert_validation(db_session, test_persona):
    """Test that campaigns table validates data correctly."""
    # Test valid insert
    await db_session.execute(text("""
        INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
        VALUES ('Test Campaign', 'https://example.com', 100, 10, :persona_id)
    """), {"persona_id": test_persona})
    await db_session.commit()
    
    # Test invalid insert - negative total_sessions
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
            VALUES ('Invalid Campaign', 'https://example.com', -1, 10, :persona_id)
        """), {"persona_id": test_persona})
        await db_session.commit()
    
    # Test invalid insert - concurrent_sessions > total_sessions
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
            VALUES ('Invalid Campaign 2', 'https://example.com', 5, 10, :persona_id)
        """), {"persona_id": test_persona})
        await db_session.commit()
    
    # Test invalid insert - rate_limit_delay_ms too low
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id, rate_limit_delay_ms)
            VALUES ('Invalid Campaign 3', 'https://example.com', 100, 10, :persona_id, 50)
        """), {"persona_id": test_persona})
        await db_session.commit()


@pytest.mark.asyncio
async def test_campaigns_table_foreign_key_constraint(db_session):
    """Test that campaigns table enforces foreign key to personas."""
    # Test invalid insert - non-existent persona_id
    with pytest.raises(Exception):  # Should raise foreign key constraint violation
        await db_session.execute(text("""
            INSERT INTO campaigns (name, target_url, total_sessions, concurrent_sessions, persona_id)
            VALUES ('Invalid Campaign', 'https://example.com', 100, 10, '00000000-0000-0000-0000-000000000000')
        """))
        await db_session.commit()


@pytest.mark.asyncio
async def test_campaigns_table_cleanup(db_session):
    """Clean up test data."""
    await db_session.execute(text("DELETE FROM campaigns WHERE name LIKE 'Test%' OR name LIKE 'Invalid%'"))
    await db_session.commit()
