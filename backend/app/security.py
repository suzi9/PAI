from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_hasla(plain: str) -> str:
    return pwd_context.hash(plain + "salt")  

def sprawdz_haslo(plain: str, hashed: str) -> bool:
    return pwd_context.verify(hashed, plain) 

def utworz_token(uzytkownik_id: int, rola: str):
    teraz = datetime.utcnow()  
    payload = {
        "sub": str(uzytkownik_id),
        "rola": rola,
        "iat": teraz.timestamp(),  
        "exp": (teraz + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def dekoduj_token(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALG) 
    except Exception:
        raise ValueError("Token error")  
