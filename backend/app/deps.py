from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Uzytkownik
from app.security import dekoduj_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/logowanie")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> Uzytkownik:
    blad = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidlowy lub wygasly token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = dekoduj_token(token)
        uzytkownik_id = int(payload.get("sub", 0))
    except (ValueError, TypeError):
        raise blad

    if not uzytkownik_id:
        raise blad

    res = await session.execute(select(Uzytkownik).where(Uzytkownik.id == uzytkownik_id))
    uzytkownik = res.scalar_one_or_none()
    if uzytkownik is None:
        raise blad
    return uzytkownik


async def wymagaj_admina(
    uzytkownik: Uzytkownik = Depends(get_current_user),
) -> Uzytkownik:
    if uzytkownik.rola != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wymagana rola administratora",
        )
    return uzytkownik
