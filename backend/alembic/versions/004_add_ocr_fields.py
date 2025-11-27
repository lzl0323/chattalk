"""add ocr fields to messages and model_type to model_configs

Revision ID: 004
Revises: 003
Create Date: 2025-11-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # 为 messages 表添加 OCR 相关字段
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('message_type', sa.String(20), server_default='text', nullable=False))
        batch_op.add_column(sa.Column('file_url', sa.String(500), nullable=True))
        batch_op.add_column(sa.Column('file_name', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('ocr_mode', sa.String(50), nullable=True))
    
    # 为 model_configs 表添加 model_type 字段
    with op.batch_alter_table('model_configs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('model_type', sa.String(20), server_default='chat', nullable=False))


def downgrade():
    # 回滚 model_configs 表
    with op.batch_alter_table('model_configs', schema=None) as batch_op:
        batch_op.drop_column('model_type')
    
    # 回滚 messages 表
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_column('ocr_mode')
        batch_op.drop_column('file_name')
        batch_op.drop_column('file_url')
        batch_op.drop_column('message_type')
