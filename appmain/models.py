from django.db import models


# Create your models here.
class KeyModel(models.Model):
    voter_id = models.CharField(max_length=10, blank=True)
    temp_id = models.TextField(max_length=256, blank=True)
    pukey = models.CharField(max_length=512, blank=True)
