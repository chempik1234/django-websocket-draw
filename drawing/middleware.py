from datetime import datetime

import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections

from django.contrib.auth.models import User

DEFAULT_ALGORITHM = "HS256"


@database_sync_to_async
def get_user_from_token(token_str_encrypted):
    try:
        payload = jwt.decode(token_str_encrypted,
                             settings.SECRET_KEY, algorithms=[DEFAULT_ALGORITHM,])
    except:
        return AnonymousUser()  # any execption => anonymous
    token_expiration_date = datetime.fromtimestamp(payload["exp"])
    if token_expiration_date < datetime.now():
        return AnonymousUser()
    try:
        user = User.objects.get(pk=payload["user_id"])
    except User.DoesNotExist:
        return AnonymousUser()
    return user


class CustomTokenMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send, *args, **kwargs):
        close_old_connections()
        try:
            query_string_params_part = scope["query_string"].decode().split('?')[-1]
            token_key = (dict((x.split('=') for x in query_string_params_part.split('&')))).get('token', None)
            # ...?token=123&a=a&b=b  -->  { "token": "123", "a": "a", "b": "b" }
        except:
            token_key = None

        scope["user"] = await get_user_from_token(token_key)
        return await super().__call__(scope, receive, send)


def jwt_auth_middleware_stack(inner):
    return CustomTokenMiddleware(inner)
