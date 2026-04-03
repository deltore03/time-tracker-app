# app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal

from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def hash_password(password: str):
    return pwd_context.hash(password)

# JWT settings
SECRET_KEY = "your-very-secret-key"  # change this to something secure!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = SessionLocal()
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()
    db.close()

    if user is None:
        raise credentials_exception

    return user

def check_admin(current_user: models.User = Depends(get_current_user)):
    #check if the user is an admin and reject if they're not.
	if not current_user.role == "admin":
		raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail="Forbidden: Admin access only"
		)
	return current_user

