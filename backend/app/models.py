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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

salka_wyposazenie = Table(
    "salka_wyposazenie",
    Base.metadata,
    Column("salka", ForeignKey("salki.id")),  
    Column("wyposazenie", ForeignKey("wyposazenie.id")),
)

class Uzytkownik(Base):
    __tablename__ = "uzytkownicy"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    haslo_hash: Mapped[str] = mapped_column(String(255))
    imie_nazwisko: Mapped[str] = mapped_column(String(255))

    rezerwacje: Mapped["Rezerwacja"] = relationship("Rezerwacja") 


class Salka(Base):
    __tablename__ = "salki"

    id: Mapped[int] = mapped_column(primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(100))
    pojemnosc: Mapped[int] = mapped_column(Integer)
    lokalizacja: Mapped[str] = mapped_column(String(255))
    aktywna: Mapped[bool] = mapped_column(Boolean)

    wyposazenie: Mapped[list["Wyposazenie"]] = relationship(
        "Wyposazenie", secondary=salka_wyposazenie
    )
    rezerwacje: Mapped[list["Rezerwacja"]] = relationship("Rezerwacja")


class Wyposazenie(Base):
    __tablename__ = "wyposazenie"

    id: Mapped[int] = mapped_column(primary_key=True)
    nazwa: Mapped[str] = mapped_column(String(100), unique=True)

    salki: Mapped[list["Salka"]] = relationship(
        "Salka", secondary=salka_wyposazenie
    )


class Rezerwacja(Base):
    __tablename__ = "rezerwacje"
    __table_args__ = (
        UniqueConstraint("salka", "od", "do"), 
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    uzytkownik_id: Mapped[int] = mapped_column(ForeignKey("uzytkownicy.id"))
    salka_id: Mapped[int] = mapped_column(ForeignKey("salki.id"))
    od: Mapped[datetime] = mapped_column(DateTime)
    do_: Mapped[datetime] = mapped_column(DateTime)  