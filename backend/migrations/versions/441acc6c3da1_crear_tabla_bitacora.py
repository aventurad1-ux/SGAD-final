"""crear tabla bitacora

Revision ID: 441acc6c3da1
Revises: 48340cb2f4fe
Create Date: 2026-10-29 13:31:14.267627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '441acc6c3da1'
down_revision = "48340cb2f4fe"
branch_labels = None
depends_on = None



def upgrade():
    op.create_table(
        "bitacora",
        sa.Column(
            "id_bitacora",
            sa.Integer(),
            sa.Identity(always=True),
            primary_key=True
        ),
        sa.Column(
            "id_usuario",
            sa.Integer(),
            nullable=True
        ),
        sa.Column(
            "accion",
            sa.String(100),
            nullable=False
        ),
        sa.Column(
            "modulo",
            sa.String(100),
            nullable=False
        ),
        sa.Column(
            "descripcion",
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            "fecha_hora",
            sa.DateTime(),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["id_usuario"],
            ["usuarios.id_usuario"],
            ondelete="SET NULL"
        )
    )


def downgrade():
    op.drop_table("bitacora")
