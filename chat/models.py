from django.db import models

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
    email = models.EmailField()
    text = models.TextField()
    

    
    
class FileLog(models.Model):
    id = models.AutoField(primary_key=True)   
    file = models.FileField(upload_to='chatfiles/%Y/%m/%d/')
    created = models.DateTimeField(auto_now_add=True)
