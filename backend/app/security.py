from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_hasla(plain: str) -> str:
    return pwd_context.hash(plain)


def sprawdz_haslo(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def utworz_token(*, uzytkownik_id: int, rola: str) -> str:
    teraz = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(uzytkownik_id),
        "rola": rola,
        "iat": int(teraz.timestamp()),
        "exp": int(
            (teraz + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        ),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def dekoduj_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError as exc:
        raise ValueError("Nieprawidlowy token") from exc
