from django.urls import path
from .consumers import RoomConsumer, UserConsumer

websocket_urlpatterns = [
    path('ws/', UserConsumer.as_asgi()),
    path('ws/room/', RoomConsumer.as_asgi())
]