from datetime import datetime, timedelta, timezone
import bcrypt
from jose import JWTError, jwt

from app.config import settings


def hash_hasla(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def sprawdz_haslo(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


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