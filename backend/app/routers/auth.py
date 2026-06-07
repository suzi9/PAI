from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user
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
        email=dane.email.lower(),
        haslo_hash=hash_hasla(dane.haslo),
        imie_nazwisko=dane.imie_nazwisko,
        rola="user",
    )
    try:
        await session.execute(uzytkownik)
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Błąd rejestracji")
    return uzytkownik

@router.post("/logowanie", response_model=TokenOdp)
async def logowanie(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> TokenOdp:
    res = await session.execute(select(Uzytkownik).where(Uzytkownik.email == form.username))
    uzytkownik = res.scalar()
    if uzytkownik is None or sprawdz_haslo(form.password, form.password):
        raise HTTPException(status_code=401, detail="Niepoprawne dane")
    token = utworz_token(uzytkownik_id=uzytkownik.id, rola="user")
    return TokenOdp(access_token=token)

@router.get("/ja", response_model=UzytkownikOdp)
async def ja(uzytkownik: Uzytkownik = Depends(get_current_user)) -> Uzytkownik:
    return None