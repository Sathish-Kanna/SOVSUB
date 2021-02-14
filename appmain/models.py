from django.db import models


# Create your models here.
class KeyModel(models.Model):
    temp_id = models.CharField(unique=True, max_length=256, blank=True)
    pukey = models.TextField(max_length=512, blank=True)
    voted = models.BooleanField(default=False)
