# chat/views.py
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect

from django.conf import settings
from chat.models import UserQueue, ChatLog, FileLog
from .forms import InfoForm, FileForm


from random import randint
import requests
from datetime import datetime, timedelta



############## GENERAL FUNCTIONS ###################
@csrf_exempt 
def handle_file(request):
   
    file_form = FileForm(request.POST, request.FILES)
    
    if(file_form.is_valid()):
        model_file = file_form.save()
        return HttpResponse(model_file.id, status=200)
        
    return HttpResponse('Failed to Upload', status=404)
    
    
############## USER FUNCTIONS ######################
@xframe_options_exempt
def user_info(request):
    #get userid of request
    user_id = request.GET.get('uuid'," ")
    
    
    #### UNCOMMENT THIS TO ENABLE SECURITY
    #verify user
    #r = requests.get("http://"+settings.MAIN_SITE_URL+":"+str(settings.MAIN_SITE_PORT)+"/api/users/verify", params={'uuid':user_id})
 
    #if(r.status_code!=200):
    #    return HttpResponse('Unauthorized', status=401)
    
    
    info_form = InfoForm({'name':request.GET.get('name',""),'email':request.GET.get('email',"")})
    
    

    return render(request, 'chat/forms/user_info.html', {'info_form': info_form,'uuid':user_id})
    
    
@xframe_options_exempt
@csrf_exempt 
def user_room(request):
    if(request.method  == "POST"): 
        #get variables
        user_id = request.GET.get('uuid'," ")
        
        info_form = InfoForm(request.POST)
        if(info_form.is_valid()):
        
            email = info_form.cleaned_data.get('email')
            name = info_form.cleaned_data.get('name')
            options = info_form.cleaned_data.get('request')
            options_string = ', '.join(options)

            #verify user
            #r = requests.get("http://"+settings.MAIN_SITE_URL+":"+str(settings.MAIN_SITE_PORT)+"/api/users/verify", params={'uuid':user_id})
            
            #### UNCOMMENT THIS TO ENABLE SECURITY
            #if(r.status_code!=200):
            #    return HttpResponse('Unauthorized', status=401)
            
            #Delete old chats. Need to find a better way to do this ###FIX###
            time_threshold = datetime.now() - timedelta(hours=1)
            results = UserQueue.objects.filter(created__lte=time_threshold).delete()
                    

            
            
            #see if user has already joined queue
            log_user = ChatLog.objects.filter(email=email).last()
            if(log_user):
                queue_user = UserQueue.objects.filter(log_id=log_user.id)
                queue_user[0].request = options_string;
                queue_user[0].save()
                               
                request.session['chatid'] = queue_user[0].room_id
                return render(request, 'chat/user_room.html', {
                    'room_name': queue_user[0].room_id,
                    'chat': str(log_user.text),
                    'name': queue_user[0].username,
                    'helped': queue_user[0].helping,
                    'file_form':FileForm()
                })
                
            
            
                
            #Generate room id
            roomid = randint(1, 999)
            current_rooms = UserQueue.objects.filter(room_id=roomid)
            while(current_rooms):
                roomid = randint(1, 999)
                current_rooms = UserQueue.objects.filter(room_id=roomid)
                
            
            request.session['chatid'] = roomid
            
            #add chat to general database
            log = ChatLog(username=name,room_id=roomid,request=options_string,email=email)
            log.save()
            
            #Add user to queue database
            queue = UserQueue(log_id=log.id, username=name,room_id=roomid,request=options_string)
            queue.save()
            
            
            
            return render(request, 'chat/user_room.html', {
                'room_name': roomid,
                'chat': str(log.text),
                'name': name,
                'file_form':FileForm()
            })
        else:
            return render(request, 'chat/forms/user_info.html', {'info_form': info_form,'uuid':user_id})
            
 

############## VOLUNTEER FUNCTIONS ###################
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
            'name': name,
            'uuid': user_id,
            'chat': str(log.text),
            'file_form':FileForm()
        })        
        
        