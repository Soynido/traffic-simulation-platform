"""Create page_visits table

Revision ID: 004
Revises: 003
Create Date: 2024-01-15 10:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Create page_visits table with all required fields and constraints."""
    op.create_table('page_visits',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('visit_order', sa.Integer(), nullable=False),
        sa.Column('arrived_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('left_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('dwell_time_ms', sa.Integer(), nullable=True),
        sa.Column('actions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('scroll_depth_percent', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name='fk_page_visits_session_id', ondelete='CASCADE'),
        sa.UniqueConstraint('session_id', 'visit_order', name='uq_page_visits_session_order')
    )
    
    # Add check constraints
    op.create_check_constraint(
        'ck_page_visits_visit_order_positive',
        'page_visits',
        'visit_order > 0'
    )
    
    op.create_check_constraint(
        'ck_page_visits_scroll_depth_range',
        'page_visits',
        'scroll_depth_percent BETWEEN 0 AND 100'
    )
    
    # Create indexes
    op.create_index('idx_page_visits_session', 'page_visits', ['session_id', 'visit_order'])
    op.create_index('idx_page_visits_url', 'page_visits', ['url'])


def downgrade():
    """Drop page_visits table."""
    op.drop_table('page_visits')
