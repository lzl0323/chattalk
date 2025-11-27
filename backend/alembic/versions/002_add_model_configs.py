"""add model_configs table

Revision ID: 002
Revises: 001
Create Date: 2024-11-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建 model_configs 表
    op.create_table(
        'model_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('api_base', sa.String(length=255), nullable=False),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quota_limit', sa.Float(), nullable=False, server_default='1000000.0'),
        sa.Column('quota_used', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('quota_reset_cron', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('ix_model_configs_name', 'model_configs', ['name'], unique=True)
    
    # 插入默认配置（使用现有的 Kimi 配置）
    op.execute("""
        INSERT INTO model_configs (name, model, api_base, api_key_encrypted, description, quota_limit, is_active)
        VALUES (
            'Kimi (默认)',
            'moonshot-v1-8k',
            'https://api.moonshot.cn/v1',
            'default-encrypted-key-please-update',
            '默认 Kimi 模型配置',
            1000000.0,
            1
        )
    """)


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_model_configs_name', table_name='model_configs')
    
    # 删除表
    op.drop_table('model_configs')
