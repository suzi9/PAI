from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# tutaj mamy rejestracje uzytkownika
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


class SalkaIn(BaseModel):
    nazwa: str = Field(min_length=1, max_length=100)
    pojemnosc: int = Field(gt=0, le=1000)
    lokalizacja: str = Field(min_length=1, max_length=255)
    aktywna: bool = True
    wyposazenie_ids: list[int] = Field(default_factory=list)


class SalkaUpdate(BaseModel):
    nazwa: str | None = Field(default=None, min_length=1, max_length=100)
    pojemnosc: int | None = Field(default=None, gt=0, le=1000)
    lokalizacja: str | None = Field(default=None, min_length=1, max_length=255)
    aktywna: bool | None = None
    wyposazenie_ids: list[int] | None = None


class SalkaOdp(BaseModel):
    id: int
    nazwa: str
    pojemnosc: int
    lokalizacja: str
    aktywna: bool
    wyposazenie: list[WyposazenieOdp]

    model_config = ConfigDict(from_attributes=True)


class RezerwacjaIn(BaseModel):
    salka_id: int
    tytul: str = Field(min_length=1, max_length=255)
    od: datetime
    do_: datetime = Field(alias="do")

    model_config = ConfigDict(populate_by_name=True)


class RezerwacjaOdp(BaseModel):
    id: int
    salka_id: int
    uzytkownik_id: int
    tytul: str
    od: datetime
    do_: datetime = Field(serialization_alias="do")
    status: str
    utworzono: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ZajetyPrzedzial(BaseModel):
    od: datetime
    do_: datetime = Field(serialization_alias="do")
