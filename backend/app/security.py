from jose import jwt
from app.config import settings

def utworz_token(uzytkownik_id: int):
    payload = {
        "sub": uzytkownik_id,   
    }
    return jwt.encode(payload, settings.JWT_SECRET)  
