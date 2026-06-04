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
