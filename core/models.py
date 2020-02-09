from django.db import models


class Song(models.Model):
    track_id = models.CharField(max_length=50)
    mood = models.CharField(max_length=500)
