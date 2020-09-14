# chat/views.py
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import get_random_string 
#channel imports
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


#forge specific import
from django.conf import settings
from chat.models import UserQueue, ChatLog, FileLog
from .forms import InfoForm, FileForm


from random import randint
import requests
from datetime import datetime, timedelta
import os



############## GENERAL FUNCTIONS ###################
###AUTH FUNCTIONS
def verify_type(user_level, required_level):
    if(required_level=="member" and (user_level=="member" or user_level=="volunteers" or user_level=="managers" or user_level=="admins")):
        return True
    if(required_level=="volunteers" and (user_level=="volunteers" or user_level=="managers" or user_level=="admins")):
        return True
    if(required_level=="managers" and (user_level=="managers" or user_level=="admins")):
        return True
    if(required_level=="admins" and user_level=="admins"):
        return True
    
    return False

def get_type(uuid):
    r = requests.get("http://"+settings.MAIN_SITE_URL+":"+str(settings.MAIN_SITE_PORT)+"/api/users/verify", params={'uuid':uuid})
    if(r.status_code!=200):
        return ""
    
    return r.content.decode()
       

def is_authorized(uuid,level):
    content = get_type(uuid)
    return verify_type(content,level)

###FILE FUNCTIONS
@xframe_options_exempt
def download_file(request):
    if(request.method == "GET"):
        user_id=request.GET.get("uuid","")
        room_id=request.GET.get("room_id","")
        file_id=request.GET.get("id","")
        
        file_log = FileLog.objects.filter(file_id=file_id)
        if(not file_log):
            return HttpResponse('Unable to download', status=400) 
        file_log = file_log.last()
        
        if(not is_authorized(user_id,"volunteers")):
            if(file_log.room_id != room_id or file_log.owner!=user_id):
                return HttpResponse('Unauthorized', status=401)
            
            
        filename = file_log.file.path
        response = FileResponse(open(filename, 'rb'))
        return response

@csrf_exempt 
def handle_file(request):
    if(request.method == "POST"):
        #generate file form
        file_form = FileForm(request.POST, request.FILES)
        
        #if file form is valid
        if(file_form.is_valid()):
            ######### REPLACE WITH FORM VALIDATION########
        
            #check file size
            file = file_form.cleaned_data['file']
            if(file.size >= 262144000):
                return HttpResponse('File to large to upload', status=400)
            
            
            #check file extension
            fileName, fileExtension = os.path.splitext(file.name)
            #if(fileExtension!=....):
            #    return HttpResponse('File to large to upload', status=400)
                
                
                
            #upload file and set owner
            model_file = file_form.save(commit=False)
            model_file.owner = request.GET.get("uuid","")
            model_file.room_id = request.GET.get("room_id","")
            model_file.file_id = get_random_string()
            model_file.owner
            model_file.save()
            
            #return file id
            return HttpResponse(model_file.file_id, status=200)
        
       
        return HttpResponse('Failed to Upload', status=400)
    else:
        return HttpResponse('Failed to Upload', status=400)
    
    
### CALENDAR FUNCTIONS
def current_volunters():
    r = requests.get("http://"+settings.MAIN_SITE_URL+":"+str(settings.MAIN_SITE_PORT)+"/api/volunteers/current")
    
    if(r.status_code!=200):
        return []
    
    return eval(r.content.decode())
    
############## USER FUNCTIONS ######################
@xframe_options_exempt
def user_info(request):
    #get userid of request
    user_id = request.GET.get('uuid'," ")
    name = request.GET.get('name',"")
    email = request.GET.get('email',"")
    
    #### UNCOMMENT THIS TO ENABLE SECURITY
    #if(not is_authorized(user_id,"member"):
    #    return HttpResponse('Unauthorized', status=401)
    session_room_id = request.session.get('room_id', -1)
    if(session_room_id != -1):
        try:
            queue_user = UserQueue.objects.get(room_id=session_room_id)
            log_user = queue_user.log
            
            if(log_user and queue_user):
                return render(request, 'chat/user_room.html', {
                    'room_name': queue_user.room_id,
                    'chat': str(log_user.text),
                    'name': queue_user.username,
                    'helped': queue_user.helping,
                    'file_form':FileForm(),
                    'uuid':user_id
                })
        except ObjectDoesNotExist:
            pass
            
    #generate form with prefilled values if present
    log_user = ChatLog.objects.filter(email=email).last()
    if(log_user):
        #get information from previous join.
        queue_user = log_user.queue
        if(queue_user):
            return render(request, 'chat/user_room.html', {
                'room_name': queue_user.room_id,
                'chat': str(log_user.text),
                'name': queue_user.username,
                'helped': queue_user.helping,
                'file_form':FileForm(),
                'uuid':user_id
            })
            
    info_form = InfoForm({'name':name,'email':email})
    
    return render(request, 'chat/forms/user_info.html', {'info_form': info_form,'uuid':user_id})
    
    
@xframe_options_exempt
@csrf_exempt 
def user_room(request):
    
    if(request.method  == "POST"): 
        #get userid variable
        user_id = request.GET.get('uuid'," ")
    
        #create form
        info_form = InfoForm(request.POST)
        if(info_form.is_valid()):
            
            #handle form data
            email = info_form.cleaned_data.get('email')
            name = info_form.cleaned_data.get('name')
            options = info_form.cleaned_data.get('request')
            options_string = ', '.join(options)

            #### UNCOMMENT THIS TO ENABLE SECURITY
            #if(not is_authorized(user_id,"member"):
            #    return HttpResponse('Unauthorized', status=401)
            
            volunteer_list = current_volunters()
            print(volunteer_list)
            
            volunteer_on_duty = False
            try:
                if( len(volunteer_list)!=0):
                    volunteer_on_duty=True
            except:
                volunteer_on_duty=False
                
            #see if user has already joined queue via email
            log_user = ChatLog.objects.filter(email=email).last()
            if(log_user):
                #get information from previous join.
                queue_user = log_user.queue
                if(queue_user):
                    queue_user.request = options_string;
                    queue_user.save()
                    
                    return render(request, 'chat/user_room.html', {
                        'room_name': queue_user.room_id,
                        'chat': str(log_user.text),
                        'name': queue_user.username,
                        'helped': queue_user.helping,
                        'file_form':FileForm(),
                        'uuid':user_id,
                        'volunteer': volunteer_on_duty
                    })
                
            #Generate room id
            roomid = randint(1, 999)
            
            #make sure id is unique
            current_rooms = UserQueue.objects.filter(room_id=roomid)
            while(current_rooms):
                roomid = randint(1, 999)
                current_rooms = UserQueue.objects.filter(room_id=roomid)
                
            
            
            #add chat to log database
            log = ChatLog(username=name,request=options_string,email=email)
            log.save()
            
            #Add user to queue database
            queue = UserQueue(log_id=log.id, username=name,room_id=roomid,request=options_string,log=log)
            queue.save()
            
            log.queue = queue
            log.save()
            
            
            channel_layer = get_channel_layer()
            
            async_to_sync(channel_layer.group_send)(
                'select_refresh',{
                    'type': 'select_message', 
                    'name': name,
                    'request': options_string,
                    'room_name': roomid,
                    'email': email,
                    'created': queue.created
                }
            )
            
            request.session['room_id'] = roomid
            
            return render(request, 'chat/user_room.html', {
                'room_name': roomid,
                'chat': str(log.text),
                'name': name,
                'file_form':FileForm(),
                'uuid':user_id,
                'volunteer': volunteer_on_duty
            })
        else:
            return render(request, 'chat/forms/user_info.html', {'info_form': info_form,'uuid':user_id})
            

@xframe_options_exempt
def user_history(request):
    if(request.method  == "GET"): 
        #get variables
        email = request.GET.get('email'," ")    
        user_id = request.GET.get('uuid'," ")
        
        #verify user
        if(not is_authorized(user_id,"member")):
            return HttpResponse('Unauthorized', status=401)
        
        #setup table information
        context = {
            "table_headers":["Created", "Request", "Link"],
            "table_rows":[],
            "uuid":user_id,
            "email":email
        }
        
        chat_history = ChatLog.objects.filter(email=email).order_by('-created')
        for chat in chat_history:
            context["table_rows"].append([chat.created, chat.request, chat.id ])
        
        return render(request, 'chat/table/chat_history.html', context)

@xframe_options_exempt
def user_history_chat(request):
    if(request.method  == "GET"): 
        #get variables
        room_id = request.GET.get('id',"")    
        email = request.GET.get('email',"")    
        user_id = request.GET.get('uuid',"")
        
        #verify user
        if(not is_authorized(user_id,"member")):
            return HttpResponse('Unauthorized', status=401)
        
        
        user = get_type(user_id)

        try:
            chat_log = ChatLog.objects.get(id=room_id)
        except ObjectDoesNotExist:
            return HttpResponse('Not Found', status=403)
        
        if(chat_log.email!=email and not verify_type(user,"managers")):
            return HttpResponse('Unauthorized', status=401)
        
        
            
            
        return render(request, 'chat/history_room.html', {
            'uuid': user_id,
            'chat': str(chat_log.text),
        }) 

############## VOLUNTEER FUNCTIONS ###################
@xframe_options_exempt
def volunteer_select(request):
    if(request.method  == "GET"): 
        #get variables
        name = request.GET.get('name',"No Name")    
        user_id = request.GET.get('uuid'," ")
        
        if(not is_authorized(user_id,"volunteers")):
            return HttpResponse('Unauthorized', status=401)
        
        #setup table information
        context = {
            "table_headers":["Created", "Name", "Email", "Request", "Being Helped", "Link"],
            "table_rows":[],
            "page_title":"Users",
            "uuid":user_id,
            "name":name
        }
        
        users_in_que = UserQueue.objects.all();
        for user_row in users_in_que:
            chat_log = user_row.log
            context["table_rows"].append([user_row.created, user_row.username, chat_log.email, user_row.request, user_row.helping, user_row.room_id ])
        
        return render(request, 'chat/table/queue_select.html', context)

@xframe_options_exempt
def volunteer_room(request):
    if(request.method  == "GET"): 
        #get variables
        name = request.GET.get('name','No Name')
        if(name==" "):
            name = "no name"
            
        user_id = request.GET.get('uuid'," ")
        room_id = request.GET.get('room_id',-1)
        
        #verify user
        if(not is_authorized(user_id,"volunteers")):
            return HttpResponse('Unauthorized', status=401)
        
        
        
        #if room was provided
        if(room_id==-1):
            return HttpResponse('Room Not Found', status=404)
        
        #get room information
        current_room = UserQueue.objects.filter(room_id=room_id)
        if(not current_room):
            return HttpResponse('Room Not Found', status=404)
        
        current_room = current_room.last()    
        
        #update to helping
        current_room.helping = True
        current_room.save()
        
        #get previous text
        log = current_room.log
        
        if(not log):
            return HttpResponse('Room Not Found', status=404)
        
        return render(request, 'chat/volunteer_room.html', {
            'room_name': room_id,
            'name': name,
            'uuid': user_id,
            'chat': str(log.text),
            'file_form':FileForm(),
        })        
      

############## Manager FUNCTIONS ###################
@xframe_options_exempt
def manager_history_chat(request):      
    if(request.method  == "GET"): 
        #get variables
        user_id = request.GET.get('uuid'," ")
        
        #verify user
        if(not is_authorized(user_id,"member")):
            return HttpResponse('Unauthorized', status=401)
        
        #setup table information
        context = {
            "table_headers":["Created", "Name", "Request", "Link"],
            "table_rows":[],
            "uuid":user_id,
            "email":""
        }
        
        chat_history = ChatLog.objects.all().order_by('-created')
        for chat in chat_history:
            context["table_rows"].append([chat.created, chat.username, chat.request, chat.id ])
        
        return render(request, 'chat/table/chat_history.html', context)
        
