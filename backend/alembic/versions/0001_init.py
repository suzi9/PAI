"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2026-06-05 06:20:00.482193

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "uzytkownicy",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("haslo_hash", sa.String(length=255), nullable=False),
        sa.Column("imie_nazwisko", sa.String(length=255), nullable=False),
        sa.Column("rola", sa.String(length=20), nullable=False, server_default="user"),
        sa.Column(
            "utworzono",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("email", name="uq_uzytkownicy_email"),
    )
    op.create_index("ix_uzytkownicy_email", "uzytkownicy", ["email"])

    op.create_table(
        "salki",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nazwa", sa.String(length=100), nullable=False),
        sa.Column("pojemnosc", sa.Integer(), nullable=False),
        sa.Column("lokalizacja", sa.String(length=255), nullable=False),
        sa.Column("aktywna", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "utworzono",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "wyposazenie",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nazwa", sa.String(length=100), nullable=False),
        sa.UniqueConstraint("nazwa", name="uq_wyposazenie_nazwa"),
    )

    op.create_table(
        "salka_wyposazenie",
        sa.Column(
            "salka_id",
            sa.Integer(),
            sa.ForeignKey("salki.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "wyposazenie_id",
            sa.Integer(),
            sa.ForeignKey("wyposazenie.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "rezerwacje",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "uzytkownik_id",
            sa.Integer(),
            sa.ForeignKey("uzytkownicy.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "salka_id",
            sa.Integer(),
            sa.ForeignKey("salki.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tytul", sa.String(length=255), nullable=False),
        sa.Column("od", sa.DateTime(timezone=True), nullable=False),
        sa.Column("do", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="aktywna"
        ),
        sa.Column(
            "utworzono",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("salka_id", "od", "do", name="uq_rezerwacja_salka_okno"),
    )
    op.create_index("ix_rezerwacje_uzytkownik_id", "rezerwacje", ["uzytkownik_id"])
    op.create_index("ix_rezerwacje_salka_id", "rezerwacje", ["salka_id"])


def downgrade() -> None:
    op.drop_index("ix_rezerwacje_salka_id", table_name="rezerwacje")
    op.drop_index("ix_rezerwacje_uzytkownik_id", table_name="rezerwacje")
    op.drop_table("rezerwacje")
    op.drop_table("salka_wyposazenie")
    op.drop_table("wyposazenie")
    op.drop_table("salki")
    op.drop_index("ix_uzytkownicy_email", table_name="uzytkownicy")
    op.drop_table("uzytkownicy")
