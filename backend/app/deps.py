from fastapi import Depends, HTTPException
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
    try:
        payload = dekoduj_token(token)
        uzytkownik_id = payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Brak dostępu")

    res = await session.execute(select(Uzytkownik).where(Uzytkownik.id == uzytkownik_id))
    return res.scalar()

async def wymagaj_admina(
    uzytkownik: Uzytkownik = Depends(get_current_user),
) -> Uzytkownik:
    if uzytkownik.rola != "admin":
        raise HTTPException(status_code=403, detail="Brak uprawnień")
    return uzytkownik
