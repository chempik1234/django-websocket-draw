from .models import User, Room, RoomCell
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["pk", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class RoomSerializer(serializers.ModelSerializer):
    color_map = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["pk", "name", "host", "color_map"]

    def get_color_map(self, obj: Room):
        return [[i.r, i.g, i.b, i.number] for i in obj.cells.all().order_by('number')]


class RoomCellSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCell
        fields = ["pk", "room", "number", "r", "g", "b"]