"""Create sessions table and session_status enum

Revision ID: 003
Revises: 002
Create Date: 2024-01-15 10:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Create session_status enum and sessions table."""
    # Create session_status enum
    session_status_enum = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed', 'timeout',
        name='session_status'
    )
    session_status_enum.create(op.get_bind())
    
    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('persona_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', session_status_enum, nullable=False, server_default='pending'),
        sa.Column('start_url', sa.String(length=500), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=False),
        sa.Column('viewport_width', sa.Integer(), nullable=False, server_default='1920'),
        sa.Column('viewport_height', sa.Integer(), nullable=False, server_default='1080'),
        sa.Column('session_duration_ms', sa.Integer(), nullable=True),
        sa.Column('pages_visited', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_actions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='fk_sessions_campaign_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], name='fk_sessions_persona_id')
    )
    
    # Create indexes
    op.create_index('idx_sessions_campaign_status', 'sessions', ['campaign_id', 'status'])
    op.create_index('idx_sessions_created_at', 'sessions', ['created_at'])


def downgrade():
    """Drop sessions table and session_status enum."""
    op.drop_table('sessions')
    op.execute('DROP TYPE session_status')
