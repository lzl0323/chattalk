"""add suggestion records table

Revision ID: 003
Revises: 002
Create Date: 2025-11-27 15:17:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # 创建推荐问题记录表
    op.create_table(
        'suggestion_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('suggestion_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('icon', sa.String(length=20), nullable=True, server_default='bolt'),
        sa.Column('is_clicked', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # 创建索引
    op.create_index('ix_suggestion_records_user_id', 'suggestion_records', ['user_id'])


def downgrade():
    # 删除索引
    op.drop_index('ix_suggestion_records_user_id', table_name='suggestion_records')
    
    # 删除表
    op.drop_table('suggestion_records')
