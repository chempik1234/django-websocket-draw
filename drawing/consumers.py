import json

from djangochannelsrestframework.decorators import action

from channels.db import database_sync_to_async
from djangochannelsrestframework.observer import model_observer

from .models import Room, RoomCell
from django.contrib.auth.models import User
from djangochannelsrestframework import mixins
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin

from .serializers import UserSerializer, RoomSerializer, RoomCellSerializer


class UserConsumer(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.PatchModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DeleteModelMixin,
                   GenericAsyncAPIConsumer):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"

    async def disconnect(self, code):
        if hasattr(self, "room_subscribe"):
            # room_subscribe - pk отслеживаемой Room, задаётся при подключении и может отсутствовать
            await self.remove_user_from_room(self.room_subscribe)
            await self.notify_users()
        await super().disconnect(code)

    @action()
    async def join_room(self, pk, **kwargs):
        self.room_subscribe = pk
        await self.add_user_to_room(pk)
        await self.notify_users()

    @action()
    async def leave_room(self, pk, **kwargs):
        await self.remove_user_from_room(pk)

    @action()
    async def set_pixel(self, number, r, g, b, **kwargs):
        obj: RoomCell = await self.get_cell(room_pk=self.room_subscribe,
                                            number=number)
        obj.r, obj.g, obj.b = r, g, b
        await database_sync_to_async(obj.save)()
        await self.channel_layer.group_send(
            f"room__{self.room_subscribe}",
            {
                'type': 'pixel_updated',
                'cell_number': number
            }
        )

    @action()
    async def subscribe_to_room(self, pk, request_id, **kwargs):
        await self.room_activity.subscribe(room=pk, request_id=request_id)

    @model_observer(RoomCell)
    async def room_activity(self, cell, observer=None, subscribing_request_ids=[], **kwargs):
        if subscribing_request_ids is None:
            subscribing_request_ids = []
        for i in subscribing_request_ids:
            cell_body = dict(request_id=i)
            cell_body.update(cell)
            await self.send_json(cell_body)

    @room_activity.groups_for_signal
    def room_activity(self, instance: RoomCell, **kwargs):
        yield f'room__{instance.room_id}'
        yield f'pk__{instance.pk}'

    @room_activity.groups_for_consumer
    def room_activity(self, room=None, **kwargs):
        if room is not None:
            yield f'room__{room}'

    @room_activity.serializer
    def room_activity(self, instance: RoomCell, action, **kwargs):
        return dict(data=RoomCellSerializer(instance).data, action=action.value, pk=instance.pk)

    async def notify_users(self):
        room: Room = await self.get_room(self.room_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'type': 'update_users',
                    'usuarios': await self.current_users(room)  # usuarios means "usernames"
                }
            )

    async def update_users(self, event: dict):
        await self.send(text_data=json.dumps({'usuarios': event["usuarios"]}))

    async def pixel_updated(self, event: dict):
        await self.send(text_data=json.dumps({'type': "pixel_updated",
                                              "cell_number": event["cell_number"]}))

    @database_sync_to_async
    def get_room(self, pk, **kwargs):
        return Room.objects.get(pk=pk)

    @database_sync_to_async
    def get_cell(self, room_pk, number):
        return RoomCell.objects.get(room__pk=room_pk, number=number)

    @database_sync_to_async
    def current_users(self, room: Room):
        return [UserSerializer(user).data for user in room.current_users.all()]

    @database_sync_to_async
    def remove_user_from_room(self, room):
        user: User = self.scope["user"]
        user.current_rooms.remove(room)

    @database_sync_to_async
    def add_user_to_room(self, pk):
        user: User = self.scope["user"]
        if not user.current_rooms.filter(pk=self.room_subscribe).exists():
            user.current_rooms.add(Room.objects.get(pk=pk))
