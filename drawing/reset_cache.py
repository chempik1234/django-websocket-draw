from django.core.cache import cache

from .models import RoomCell, Room


def make_key_for_cell(room_pk, number):
    return f"cell-{room_pk}-{number}"


def reset_rooms_cache():
    all_rooms = Room.objects.all().values("pk", "name", "host")
    cache.delete('rooms')
    cache.set('rooms', all_rooms, 60 * 60)  # 1h


def reset_cache_cell(room_pk, number):
    cell = RoomCell.objects.get(room__pk=room_pk, number=number)
    cell_key = make_key_for_cell(room_pk, number)
    cache.delete(cell_key)
    cache.set(cell_key, cell, 60 * 60)  # 1h
    return cell
