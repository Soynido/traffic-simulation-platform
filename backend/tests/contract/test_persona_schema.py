"""
Contract test for personas table schema.
Tests database schema compliance for persona entity.
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
async def test_personas_table_exists(db_session):
    """Test that personas table exists with correct structure."""
    # Check table exists
    result = await db_session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'personas'
    """))
    assert result.fetchone() is not None, "personas table should exist"


@pytest.mark.asyncio
async def test_personas_table_columns(db_session):
    """Test that personas table has all required columns with correct types."""
    result = await db_session.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'personas'
        ORDER BY ordinal_position
    """))
    
    columns = {row[0]: {'type': row[1], 'nullable': row[2] == 'YES', 'default': row[3]} 
              for row in result.fetchall()}
    
    # Required columns
    expected_columns = {
        'id': {'type': 'uuid', 'nullable': False, 'default': True},
        'name': {'type': 'character varying', 'nullable': False, 'default': False},
        'description': {'type': 'text', 'nullable': True, 'default': False},
        'session_duration_min': {'type': 'integer', 'nullable': False, 'default': False},
        'session_duration_max': {'type': 'integer', 'nullable': False, 'default': False},
        'pages_min': {'type': 'integer', 'nullable': False, 'default': False},
        'pages_max': {'type': 'integer', 'nullable': False, 'default': False},
        'actions_per_page_min': {'type': 'integer', 'nullable': False, 'default': True},
        'actions_per_page_max': {'type': 'integer', 'nullable': False, 'default': True},
        'scroll_probability': {'type': 'numeric', 'nullable': False, 'default': True},
        'click_probability': {'type': 'numeric', 'nullable': False, 'default': True},
        'typing_probability': {'type': 'numeric', 'nullable': False, 'default': True},
        'created_at': {'type': 'timestamp with time zone', 'nullable': False, 'default': True},
        'updated_at': {'type': 'timestamp with time zone', 'nullable': False, 'default': True}
    }
    
    for col_name, expected in expected_columns.items():
        assert col_name in columns, f"Column {col_name} should exist"
        col = columns[col_name]
        assert col['type'] == expected['type'], f"Column {col_name} should have type {expected['type']}, got {col['type']}"
        assert col['nullable'] == expected['nullable'], f"Column {col_name} nullable should be {expected['nullable']}"
        if expected['default']:
            assert col['default'] is not None, f"Column {col_name} should have default value"


@pytest.mark.asyncio
async def test_personas_table_constraints(db_session):
    """Test that personas table has correct constraints."""
    # Test primary key
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'personas' 
        AND constraint_type = 'PRIMARY KEY'
    """))
    assert result.fetchone() is not None, "personas table should have primary key"
    
    # Test unique constraint on name
    result = await db_session.execute(text("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints 
        WHERE table_schema = 'public' AND table_name = 'personas' 
        AND constraint_type = 'UNIQUE'
    """))
    assert result.fetchone() is not None, "personas table should have unique constraint on name"
    
    # Test check constraints
    result = await db_session.execute(text("""
        SELECT constraint_name, check_clause
        FROM information_schema.check_constraints 
        WHERE constraint_schema = 'public' 
        AND constraint_name LIKE '%personas%'
    """))
    check_constraints = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have constraints for positive values and probability ranges
    assert any('session_duration_min > 0' in clause for clause in check_constraints.values()), "Should have constraint for positive session_duration_min"
    assert any('session_duration_max >= session_duration_min' in clause for clause in check_constraints.values()), "Should have constraint for logical duration range"
    assert any('scroll_probability BETWEEN 0 AND 1' in clause for clause in check_constraints.values()), "Should have constraint for probability range"


@pytest.mark.asyncio
async def test_personas_table_indexes(db_session):
    """Test that personas table has required indexes."""
    result = await db_session.execute(text("""
        SELECT indexname, indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public' AND tablename = 'personas'
    """))
    
    indexes = {row[0]: row[1] for row in result.fetchall()}
    
    # Should have unique index on name
    assert any('UNIQUE' in idx_def and 'name' in idx_def for idx_def in indexes.values()), "Should have unique index on name column"


@pytest.mark.asyncio
async def test_personas_table_insert_validation(db_session):
    """Test that personas table validates data correctly."""
    # Test valid insert
    await db_session.execute(text("""
        INSERT INTO personas (name, session_duration_min, session_duration_max, pages_min, pages_max)
        VALUES ('Test Persona', 60, 120, 1, 5)
    """))
    await db_session.commit()
    
    # Test invalid insert - negative duration
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO personas (name, session_duration_min, session_duration_max, pages_min, pages_max)
            VALUES ('Invalid Persona', -1, 120, 1, 5)
        """))
        await db_session.commit()
    
    # Test invalid insert - probability out of range
    with pytest.raises(Exception):  # Should raise constraint violation
        await db_session.execute(text("""
            INSERT INTO personas (name, session_duration_min, session_duration_max, pages_min, pages_max, scroll_probability)
            VALUES ('Invalid Persona 2', 60, 120, 1, 5, 1.5)
        """))
        await db_session.commit()
    
    # Test invalid insert - duplicate name
    with pytest.raises(Exception):  # Should raise unique constraint violation
        await db_session.execute(text("""
            INSERT INTO personas (name, session_duration_min, session_duration_max, pages_min, pages_max)
            VALUES ('Test Persona', 60, 120, 1, 5)
        """))
        await db_session.commit()


@pytest.mark.asyncio
async def test_personas_table_cleanup(db_session):
    """Clean up test data."""
    await db_session.execute(text("DELETE FROM personas WHERE name LIKE 'Test%' OR name LIKE 'Invalid%'"))
    await db_session.commit()
