from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from db import db_dependency
from helpers import authenticate_user, create_access_token, bcrypt_context
from models import User
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

class CreateUserRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: db_dependency,
    create_user_request: CreateUserRequest
):
    create_user_model = User(
        username=create_user_request.username,
        hashed_pass=bcrypt_context.hash(create_user_request.password)
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm,
                             Depends()], db: db_dependency):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not validated.")
    
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    
    return {"access_token": token, "token_type": "bearer"}

