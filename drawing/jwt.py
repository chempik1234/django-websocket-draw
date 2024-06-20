from datetime import timedelta
import datetime

import jwt
from django.conf import settings
from django.contrib.auth.models import User

from .middleware import DEFAULT_ALGORITHM


def create_token(user: User) -> dict:
    expiration_delta = timedelta(minutes=60)
    return {
        "access_token": create_access_token(data={"user_id": user.pk}, expiration_delta=expiration_delta),
        "token_type": "Token"
    }


ACCESS_TOKEN_SUBJECT = "accept"


def create_access_token(data: dict, expiration_delta):
    dict_to_encode = data.copy()
    if expiration_delta:
        expires = datetime.datetime.now(datetime.UTC) + expiration_delta
    else:
        expires = datetime.datetime.now(datetime.UTC) + timedelta(minutes=15)
    dict_to_encode.update({"sub": ACCESS_TOKEN_SUBJECT, "exp": expires})
    return jwt.encode(dict_to_encode, settings.SECRET_KEY, algorithm=DEFAULT_ALGORITHM)
