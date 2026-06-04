from sqlalchemy import Column, Integer, String
from app.db import Base

class Uzytkownik(Base):
    __tablename__ = "uzytkownicy"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    haslo_hash = Column(String)
