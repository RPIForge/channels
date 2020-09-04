from django.db import models
from django.conf import settings
import os

class UserQueue(models.Model):
    log = models.ForeignKey("ChatLog", null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    room_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    request =  models.CharField(max_length=255)
    helping = models.BooleanField(default=False)
    
    
class ChatLog(models.Model):
    id = models.AutoField(primary_key=True)
    queue = models.ForeignKey("UserQueue",  null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=255)
    request =  models.CharField(max_length=255)
    email = models.EmailField()
    text = models.TextField()
    

    
    
class FileLog(models.Model):
    id = models.AutoField(primary_key=True)   
    file = models.FileField(upload_to='chatfiles/%Y/%m/%d/')
    owner = models.CharField(max_length=255)
    room_id = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    
    def delete(self, *args, **kwargs):
        path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        if(os.path.exists(path)):
            os.remove(path)
            
        super(FileLog,self).delete(*args,**kwargs)
    
