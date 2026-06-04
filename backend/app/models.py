from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db import Base

class Uzytkownik(Base):
    __tablename__ = "uzytkownicy"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    haslo_hash = Column(String(255))
    imie_nazwisko = Column(String(255))

    rezerwacje = relationship("Rezerwacja")


class Salka(Base):
    __tablename__ = "salki"

    id = Column(Integer, primary_key=True)
    nazwa = Column(String(100))
    pojemnosc = Column(Integer)
    lokalizacja = Column(String(255))
    aktywna = Column(Boolean)

    wyposazenie = relationship("Wyposazenie")


class Wyposazenie(Base):
    __tablename__ = "wyposazenie"

    id = Column(Integer, primary_key=True)
    nazwa = Column(String(100), unique=True)


class Rezerwacja(Base):
    __tablename__ = "rezerwacje"

    id = Column(Integer, primary_key=True)
    uzytkownik_id = Column(Integer, ForeignKey("uzytkownicy"))
    salka_id = Column(Integer, ForeignKey("salki"))
    od = Column(DateTime)
    do = Column(DateTime)