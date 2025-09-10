"""Create actions table and action_type enum

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 10:04:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """Create action_type enum and actions table."""
    # Create action_type enum
    action_type_enum = postgresql.ENUM(
        'click', 'double_click', 'right_click',
        'scroll', 'scroll_to_element',
        'type', 'clear', 'select',
        'hover', 'drag_and_drop',
        'key_press', 'page_load', 'page_unload',
        name='action_type'
    )
    action_type_enum.create(op.get_bind())
    
    # Create actions table
    op.create_table('actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('page_visit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', action_type_enum, nullable=False),
        sa.Column('element_selector', sa.Text(), nullable=True),
        sa.Column('element_text', sa.Text(), nullable=True),
        sa.Column('coordinates_x', sa.Integer(), nullable=True),
        sa.Column('coordinates_y', sa.Integer(), nullable=True),
        sa.Column('input_value', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('action_order', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['page_visit_id'], ['page_visits.id'], name='fk_actions_page_visit_id', ondelete='CASCADE'),
        sa.UniqueConstraint('page_visit_id', 'action_order', name='uq_actions_page_visit_order')
    )
    
    # Add check constraints
    op.create_check_constraint(
        'ck_actions_action_order_positive',
        'actions',
        'action_order > 0'
    )
    
    # Create indexes
    op.create_index('idx_actions_page_visit', 'actions', ['page_visit_id', 'action_order'])
    op.create_index('idx_actions_type_timestamp', 'actions', ['action_type', 'timestamp'])


def downgrade():
    """Drop actions table and action_type enum."""
    op.drop_table('actions')
    op.execute('DROP TYPE action_type')
