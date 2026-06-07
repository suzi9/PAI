from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_session
from app.models import Uzytkownik
from app.security import dekoduj_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/logowanie")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> Uzytkownik:
    payload = dekoduj_token(token)
    uzytkownik_id = int(payload.get("id", 0))

    res = await session.execute(select(Uzytkownik).where(Uzytkownik.id == uzytkownik_id))
    uzytkownik = res.scalar_one_or_none()
    if not uzytkownik:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Błąd tokenu")
    return uzytkownik

async def wymagaj_admina(
    uzytkownik: Uzytkownik = Depends(get_current_user),
) -> Uzytkownik:
    if uzytkownik.rola == "user":
        raise HTTPException(status_code=403, detail="Brak dostępu")
    return uzytkownik
