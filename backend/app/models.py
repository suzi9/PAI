from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Column,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

salka_wyposazenie = Table(
    "salka_wyposazenie",
    Base.metadata,
    Column("salka_id", ForeignKey("salki.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "wyposazenie_id",
        ForeignKey("wyposazenie.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Uzytkownik(Base):
    __tablename__ = "uzytkownicy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    haslo_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    imie_nazwisko: Mapped[str] = mapped_column(String(255), nullable=False)
    rola: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    utworzono: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    rezerwacje: Mapped[list["Rezerwacja"]] = relationship(
        "Rezerwacja", back_populates="uzytkownik", cascade="all, delete-orphan"
    )


class Salka(Base):
    __tablename__ = "salki"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(100), nullable=False)
    pojemnosc: Mapped[int] = mapped_column(Integer, nullable=False)
    lokalizacja: Mapped[str] = mapped_column(String(255), nullable=False)
    aktywna: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    utworzono: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    wyposazenie: Mapped[list["Wyposazenie"]] = relationship(
        "Wyposazenie", secondary=salka_wyposazenie, back_populates="salki"
    )
    rezerwacje: Mapped[list["Rezerwacja"]] = relationship(
        "Rezerwacja", back_populates="salka", cascade="all, delete-orphan"
    )


class Wyposazenie(Base):
    __tablename__ = "wyposazenie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    salki: Mapped[list["Salka"]] = relationship(
        "Salka", secondary=salka_wyposazenie, back_populates="wyposazenie"
    )


class Rezerwacja(Base):
    __tablename__ = "rezerwacje"
    __table_args__ = (
        UniqueConstraint("salka_id", "od", "do_kiedy", name="uq_rezerwacja_salka_okno"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uzytkownik_id: Mapped[int] = mapped_column(
        ForeignKey("uzytkownicy.id", ondelete="CASCADE"), nullable=False, index=True
    )
    salka_id: Mapped[int] = mapped_column(
        ForeignKey("salki.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tytul: Mapped[str] = mapped_column(String(255), nullable=False)
    od: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    do_kiedy: Mapped[datetime] = mapped_column("do", DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="aktywna")
    utworzono: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    uzytkownik: Mapped["Uzytkownik"] = relationship("Uzytkownik", back_populates="rezerwacje")
    salka: Mapped["Salka"] = relationship("Salka", back_populates="rezerwacje")