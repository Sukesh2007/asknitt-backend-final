"""update id column

Revision ID: 79d613c20ec9
Revises: 
Create Date: 2026-08-11 17:45:55.513252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79d613c20ec9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS questions_id_seq
        OWNED BY questions.id
    """)

    op.execute("""
        SELECT setval(
            'questions_id_seq',
            COALESCE((SELECT MAX(id) FROM questions), 0) + 1,
            false
        )
    """)

    op.execute("""
        ALTER TABLE questions
        ALTER COLUMN id SET DEFAULT nextval('questions_id_seq')
    """)


def downgrade() -> None:

    op.execute("""
        ALTER TABLE questions
        ALTER COLUMN id DROP DEFAULT
    """)

    op.execute("""
        DROP SEQUENCE IF EXISTS questions_id_seq
    """)