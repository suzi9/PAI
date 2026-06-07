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

@router.post("/logowanie", response_model=TokenOdp)
async def logowanie(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> TokenOdp:
    res = await session.execute(select(Uzytkownik).where(Uzytkownik.email == form.username))
    uzytkownik = res.scalar_one_or_none()
    if not uzytkownik or sprawdz_haslo(uzytkownik.haslo_hash, form.password):
        raise HTTPException(status_code=401, detail="Błąd logowania")
    token = utworz_token(uzytkownik_id=uzytkownik.id, rola=uzytkownik.rola)
    return TokenOdp(access_token=token)

@router.get("/ja", response_model=UzytkownikOdp)
async def ja(uzytkownik: Uzytkownik = Depends()):
    return uzytkownik
