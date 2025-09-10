"""Create analytics tables (session_analytics and campaign_analytics)

Revision ID: 006
Revises: 005
Create Date: 2024-01-15 10:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Create session_analytics and campaign_analytics tables."""
    
    # Create session_analytics table
    op.create_table('session_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('persona_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Timing metrics
        sa.Column('total_duration_ms', sa.Integer(), nullable=False),
        sa.Column('avg_page_dwell_time_ms', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('median_page_dwell_time_ms', sa.Integer(), nullable=True),
        
        # Navigation metrics
        sa.Column('pages_visited', sa.Integer(), nullable=False),
        sa.Column('navigation_depth', sa.Integer(), nullable=False),
        sa.Column('bounce_rate', sa.Numeric(precision=3, scale=2), nullable=True),
        
        # Interaction metrics
        sa.Column('total_actions', sa.Integer(), nullable=False),
        sa.Column('actions_per_page', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('click_through_rate', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('scroll_engagement', sa.Numeric(precision=3, scale=2), nullable=True),
        
        # Behavioral patterns
        sa.Column('action_variance', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('rhythm_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('pause_distribution', postgresql.JSONB(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name='fk_session_analytics_session_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='fk_session_analytics_campaign_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['persona_id'], ['personas.id'], name='fk_session_analytics_persona_id'),
        sa.UniqueConstraint('session_id', name='uq_session_analytics_session_id')
    )
    
    # Create campaign_analytics table
    op.create_table('campaign_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Completion metrics
        sa.Column('total_sessions', sa.Integer(), nullable=False),
        sa.Column('completed_sessions', sa.Integer(), nullable=False),
        sa.Column('failed_sessions', sa.Integer(), nullable=False),
        sa.Column('success_rate', sa.Numeric(precision=3, scale=2), nullable=False),
        
        # Performance metrics
        sa.Column('avg_session_duration_ms', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('avg_pages_per_session', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('avg_actions_per_session', sa.Numeric(precision=6, scale=2), nullable=True),
        
        # Quality metrics
        sa.Column('avg_rhythm_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('behavioral_variance', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('detection_risk_score', sa.Numeric(precision=3, scale=2), nullable=True),
        
        # Resource usage
        sa.Column('total_runtime_ms', sa.BigInteger(), nullable=True),
        sa.Column('avg_cpu_usage', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('peak_memory_mb', sa.Integer(), nullable=True),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='fk_campaign_analytics_campaign_id', ondelete='CASCADE'),
        sa.UniqueConstraint('campaign_id', name='uq_campaign_analytics_campaign_id')
    )
    
    # Create indexes for session_analytics
    op.create_index('idx_session_analytics_campaign', 'session_analytics', ['campaign_id'])
    op.create_index('idx_session_analytics_persona', 'session_analytics', ['persona_id'])
    op.create_index('idx_session_analytics_created_at', 'session_analytics', ['created_at'])
    
    # Create indexes for campaign_analytics
    op.create_index('idx_campaign_analytics_updated', 'campaign_analytics', ['updated_at'])


def downgrade():
    """Drop analytics tables."""
    op.drop_table('campaign_analytics')
    op.drop_table('session_analytics')
