"""Create personas table

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create personas table with all required fields and constraints."""
    op.create_table('personas',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('session_duration_min', sa.Integer(), nullable=False),
        sa.Column('session_duration_max', sa.Integer(), nullable=False),
        sa.Column('pages_min', sa.Integer(), nullable=False),
        sa.Column('pages_max', sa.Integer(), nullable=False),
        sa.Column('actions_per_page_min', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('actions_per_page_max', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('scroll_probability', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.8'),
        sa.Column('click_probability', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.6'),
        sa.Column('typing_probability', sa.Numeric(precision=3, scale=2), nullable=False, server_default='0.1'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Add check constraints
    op.create_check_constraint(
        'ck_personas_session_duration_min_positive',
        'personas',
        'session_duration_min > 0'
    )
    
    op.create_check_constraint(
        'ck_personas_session_duration_max_gte_min',
        'personas',
        'session_duration_max >= session_duration_min'
    )
    
    op.create_check_constraint(
        'ck_personas_pages_min_positive',
        'personas',
        'pages_min > 0'
    )
    
    op.create_check_constraint(
        'ck_personas_pages_max_gte_min',
        'personas',
        'pages_max >= pages_min'
    )
    
    op.create_check_constraint(
        'ck_personas_scroll_probability_range',
        'personas',
        'scroll_probability BETWEEN 0 AND 1'
    )
    
    op.create_check_constraint(
        'ck_personas_click_probability_range',
        'personas',
        'click_probability BETWEEN 0 AND 1'
    )
    
    op.create_check_constraint(
        'ck_personas_typing_probability_range',
        'personas',
        'typing_probability BETWEEN 0 AND 1'
    )


def downgrade():
    """Drop personas table."""
    op.drop_table('personas')
