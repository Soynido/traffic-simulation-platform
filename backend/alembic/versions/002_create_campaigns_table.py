"""Create campaigns table and campaign_status enum

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create campaign_status enum and campaigns table."""
    # Create campaign_status enum
    campaign_status_enum = postgresql.ENUM(
        'pending', 'running', 'paused', 'completed', 'failed',
        name='campaign_status'
    )
    campaign_status_enum.create(op.get_bind())
    
    # Create campaigns table
    op.create_table('campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_url', sa.String(length=500), nullable=False),
        sa.Column('total_sessions', sa.Integer(), nullable=False),
        sa.Column('concurrent_sessions', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('status', campaign_status_enum, nullable=False, server_default='pending'),
        sa.Column('persona_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rate_limit_delay_ms', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('user_agent_rotation', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('respect_robots_txt', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], name='fk_campaigns_persona_id')
    )
    
    # Add check constraints
    op.create_check_constraint(
        'ck_campaigns_total_sessions_positive',
        'campaigns',
        'total_sessions > 0'
    )
    
    op.create_check_constraint(
        'ck_campaigns_concurrent_sessions_positive',
        'campaigns',
        'concurrent_sessions > 0'
    )
    
    op.create_check_constraint(
        'ck_campaigns_concurrent_sessions_lte_total',
        'campaigns',
        'concurrent_sessions <= total_sessions'
    )
    
    op.create_check_constraint(
        'ck_campaigns_rate_limit_delay_minimum',
        'campaigns',
        'rate_limit_delay_ms >= 100'
    )
    
    # Create indexes
    op.create_index('idx_campaigns_status_created', 'campaigns', ['status', 'created_at'])


def downgrade():
    """Drop campaigns table and campaign_status enum."""
    op.drop_table('campaigns')
    op.execute('DROP TYPE campaign_status')
