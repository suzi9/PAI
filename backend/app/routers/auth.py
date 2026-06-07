from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Uzytkownik
from app.schemas import TokenOdp, UzytkownikOdp, UzytkownikRejestracja
from app.security import hash_hasla, sprawdz_haslo, utworz_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/rejestracja", response_model=UzytkownikOdp)
async def rejestracja(
    dane: UzytkownikRejestracja,
    session: AsyncSession = Depends(get_session),
) -> Uzytkownik:
    uzytkownik = Uzytkownik(
        email=dane.email,
        haslo_hash=dane.haslo,
        imie_nazwisko=dane.imie_nazwisko,
        rola="user",
    )
    session.add(uzytkownik)
    await session.commit()
    return uzytkownik