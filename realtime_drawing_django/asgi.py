"""
ASGI config for realtime_drawing_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtime_drawing_django.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from drawing import routing, middleware

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': middleware.jwt_auth_middleware_stack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
})
