# chat/views.py
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponse, HttpResponseRedirect

from django.conf import settings
from chat.models import UserQueue
from chat.models import ChatLog


from random import randint
import requests
from datetime import datetime, timedelta

def index(request):
    return render(request, 'chat/index.html', {})

@xframe_options_exempt
def user_room(request):
    if(request.method  == "GET"): 
        #get variables
        name = request.GET.get('name'," ")    
        user_id = request.GET.get('uuid'," ")
        options = request.GET.get('request','')
        email = request.GET.get('email','')
        
        #verify user
        r = requests.get("http://"+settings.MAIN_SITE_URL+":"+str(settings.MAIN_SITE_PORT)+"/api/users/verify", params={'uuid':user_id})
        
        #### UNCOMMENT THIS TO ENABLE SECURITY
        #if(r.status_code!=200):
        #    return HttpResponse('Unauthorized', status=401)
        
        #Delete old chats. Need to find a better way to do this ###FIX###
        time_threshold = datetime.now() - timedelta(hours=1)
        results = UserQueue.objects.filter(created__lte=time_threshold).delete()
                
        if 'chatid' in request.session:
            print("rejoining")
            return render(request, 'chat/user_room.html', {
                'room_name': request.session['chatid']
            })
        
        
        
        #see if user has already joined queue
        current_users = UserQueue.objects.filter(username=name)
        if(current_users):
            current_users[0].request = options;
            current_users[0].save()
            
            log = ChatLog.objects.get(id=current_users[0].log_id)
            
            request.session['chatid'] = current_users[0].room_id
            return render(request, 'chat/user_room.html', {
                'room_name': current_users[0].room_id,
                'chat': str(log.text)
            })
            
         
        
            
        #Generate room id
        roomid = randint(1, 999)
        current_rooms = UserQueue.objects.filter(room_id=roomid)
        while(current_rooms):
            roomid = randint(1, 999)
            current_rooms = UserQueue.objects.filter(room_id=roomid)
            
        
        request.session['chatid'] = roomid
        
        #add chat to general database
        log = ChatLog(username=name,room_id=roomid,request=options,email=email)
        log.save()
        
        #Add user to queue database
        queue = UserQueue(log_id=log.id, username=name,room_id=roomid,request=options)
        queue.save()
        
        
        
        return render(request, 'chat/user_room.html', {
            'room_name': roomid,
            'chat': str(log.text)
        })
        
@xframe_options_exempt
def volunteer_select(request):
    if(request.method  == "GET"): 
        #get variables
        name = request.GET.get('name'," ")    
        user_id = request.GET.get('uuid'," ")
        
        #verify user
        r = requests.get("http://"+settings.MAIN_SITE_URL+":"+str(settings.MAIN_SITE_PORT)+"/api/users/verify", params={'uuid':user_id})
       
        if(r.status_code!=200):
            return HttpResponse('Unauthorized', status=401)
            
        #if not volunteer or above
        content = r.content.decode()
        if(content != "volunteers" and content != "managers" and content != "admins"):
            return HttpResponse('Unauthorized', status=401)
        
        context = {
            "table_headers":["Name", "Request", "Being Helped", "Link"],
            "table_rows":[],
            "page_title":"Users",
            "uuid":user_id,
            "name":name
        }
        
        users_in_que = UserQueue.objects.all();
        for user_row in users_in_que:
            context["table_rows"].append([user_row.username, user_row.request, user_row.helping, user_row.room_id ])
        
        return render(request, 'chat/volunteer.html', context)

@xframe_options_exempt
def volunteer_room(request):
    if(request.method  == "GET"): 
        #get variables
        name = request.GET.get('name','no name')
        if(name==" "):
            name = "no name"
            
        user_id = request.GET.get('uuid'," ")
        room_id = request.GET.get('room_id',-1)
        
        #verify user
        r = requests.get("http://"+settings.MAIN_SITE_URL+":"+str(settings.MAIN_SITE_PORT)+"/api/users/verify", params={'uuid':user_id})
       
        if(r.status_code!=200):
            return HttpResponse('Unauthorized', status=401)
            
        #if not volunteer or above
        content = r.content.decode()
        if(content != "volunteers" and content != "managers" and content != "admins"):
            return HttpResponse('Unauthorized', status=401)
        
        if(room_id==-1):
            return HttpResponse('Room Not Found', status=404)
        
        
        
        #current_rooms = UserQueue.objects.filter(room_id=room_id).delete()
        current_room = UserQueue.objects.get(room_id=room_id)
        current_room.helping = True
        current_room.save()
        
        log = ChatLog.objects.get(id=current_room.log_id)
        
        
        return render(request, 'chat/volunteer_room.html', {
            'room_name': room_id,
            'volunteer_name': name,
            'uuid': user_id,
            'chat': str(log.text)
        })        
        
        