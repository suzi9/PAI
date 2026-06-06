from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UzytkownikRejestracja(BaseModel):
    email: EmailStr
    haslo: str = Field(min_length=6, max_length=128)
    imie_nazwisko: str = Field(min_length=2, max_length=255)


class UzytkownikLogowanie(BaseModel):
    email: EmailStr
    haslo: str


class UzytkownikOdp(BaseModel):
    id: int
    email: EmailStr
    imie_nazwisko: str
    rola: str
    utworzono: datetime

    model_config = ConfigDict(from_attributes=True)