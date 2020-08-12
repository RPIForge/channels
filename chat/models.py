from django.db import models
from jsonfield import JSONField

class UserQueue(models.Model):
    log_id = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    room_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    request =  models.CharField(max_length=255)
    helping = models.BooleanField(default=False)
    
    
class ChatLog(models.Model):
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    room_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    request =  models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    text = models.TextField()
    