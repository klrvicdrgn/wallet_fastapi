from datetime import timedelta, datetime
from typing import Annotated
from fastapi import Depends, HTTPException
from starlette import status
from models import User
from jose import jwt, JWTError
from os import environ
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import requests


SECRET_KEY = environ["SECRET_KEY"]
ALGORITHM = environ["ALGORITHM"]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_pass):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {
        "sub": username,
        "id": user_id,
        "exp": datetime.now() + expires_delta,
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")


def get_conversion_rates():
    json_data = requests.get("https://api.nbp.pl/api/exchangerates/tables/C/?format=json").json()
    return {r['code']: r['ask'] for r in json_data[0]["rates"]}

