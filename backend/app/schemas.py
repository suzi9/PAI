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


class TokenOdp(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class WyposazenieIn(BaseModel):
    nazwa: str = Field(min_length=1, max_length=100)


class WyposazenieOdp(BaseModel):
    id: int
    nazwa: str

    model_config = ConfigDict(from_attributes=True)