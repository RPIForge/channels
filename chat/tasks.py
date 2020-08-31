from celery.task.schedules import crontab
from celery.decorators import periodic_task

from datetime import datetime, timedelta
from .models import FileLog

@periodic_task(run_every=(crontab(hour='0')), name="remove_old_media", ignore_result=True)
def remove_media():
    print("Removing Media")
    
    time_threshold = datetime.now() - timedelta(weeks=1)
    item_list = FileLog.objects.filter(created__lte=time_threshold)
        
    print(time_threshold)
    print(item_list)
    
    for files in item_list:
        files.delete()
        
    return True
