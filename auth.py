import asyncio
import base64
import datetime
import itertools
import json
import random
import string
import uuid

from fastapi import (APIRouter, Depends, FastAPI, HTTPException, WebSocket,
                     status)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from requests_oauthlib import OAuth2Session

with open(".secrets/client_secret.json") as fp:
    OAUTH2_CLIENT_SECRET = json.load(fp)["web"]


with open(".secrets/jwt_secret.json") as fp:
    SECRET_KEY = json.load(fp)["secret_key"]

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

api = APIRouter()
scheme = HTTPBearer()

class Auth(BaseModel):
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str


def get_current_user(auth: HTTPAuthorizationCredentials = Depends(scheme)):
    credentials_exception = HTTPException(status.HTTP_403_FORBIDDEN)
    try:
        payload = jwt.decode(auth.credentials, SECRET_KEY)
        if payload is None or not payload.get("verified_email"):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return payload


@api.post("/login")
def login(auth: Auth) -> Token:
    google = OAuth2Session(
        client_id=OAUTH2_CLIENT_SECRET["client_id"],
        auto_refresh_url=OAUTH2_CLIENT_SECRET["token_uri"],
        auto_refresh_kwargs=OAUTH2_CLIENT_SECRET,
        redirect_uri="http://localhost:3000",
        scope=SCOPES,
    )

    google.fetch_token(
        token_url=OAUTH2_CLIENT_SECRET["token_uri"],
        code=auth.code,
        client_secret=OAUTH2_CLIENT_SECRET["client_secret"],
    )

    resp = google.get("https://www.googleapis.com/oauth2/v2/userinfo")
    access_token = jwt.encode(resp.json(), SECRET_KEY)
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/me")
def me(user = Depends(get_current_user)):
    return user
