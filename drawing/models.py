from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms", null=False, blank=False)
    current_users = models.ManyToManyField(User, related_name="current_rooms", blank=True)

    def __str__(self):
        return f"Room({self.name} {self.host})"


class RoomCell(models.Model):
    number = models.IntegerField(null=False, blank=False)
    room = models.ForeignKey(Room, null=False, blank=False, on_delete=models.CASCADE, related_name="cells")
    r = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0), MaxValueValidator(255)])
    g = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0), MaxValueValidator(255)])
    b = models.IntegerField(null=False, blank=False, validators=[MinValueValidator(0), MaxValueValidator(255)])

    class Meta:
        unique_together = ['number', 'room']
