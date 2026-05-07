from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# ---------------- PASSWORD ----------------
def hash_password(p):
    return pwd.hash(p)

def verify(p, h):
    return pwd.verify(p, h)

# ---------------- JWT CREATE ----------------
def create_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# ---------------- JWT VERIFY ----------------
def get_current_user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")