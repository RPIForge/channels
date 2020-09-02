# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import UserQueue
from chat.models import ChatLog
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import StopConsumer


from .views import is_authorized
from urllib.parse import parse_qs


class ChatConsumer(AsyncWebsocketConsumer):
    name = ""
    active = False
    
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': self.name+" has left the chat!",
                    'name': "system"
                }
            )
   
        await self.add_text("system,"+self.name+" has left the chat!")
   
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        raise StopConsumer 
    
    #### RECEIVE HELPER ####
    @database_sync_to_async
    def delete_room(self):
        return UserQueue.objects.filter(room_id=self.room_name).delete()
    
    @database_sync_to_async
    def add_text(self,string_data):
        try:
            room = UserQueue.objects.get(room_id=self.room_name)
            log = ChatLog.objects.get(id=room.log_id)
        except ObjectDoesNotExist:
            return None
        
        log.text = log.text + string_data + "|||"
        return log.save()
    
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if("volunteer_finish" in text_data_json):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': self.name+" has closed the chat. You may leave whenever",
                    'name': "system",
                    'volunteer_finish': True
                }
            )
            
            
            await self.delete_room()
            
        elif("volunteer_info" in text_data_json):
            self.active=True
            
            if(self.name==""):
                self.name = text_data_json["volunteer_info"]
            
            message = str(self.name+" has joined the chat!")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message':message,
                    'name': "system",
                    'volunteer': True
                    
                }
            )
            
            await self.add_text(str("system,"+message)) 
            
                   
        elif("message" in text_data_json):
            message = text_data_json['message']
            name = text_data_json['name']
            
            if(self.name=="" and name!='system'):
                self.name = name
            
            await self.add_text(str(name+','+message))
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'name': name
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))


class SelectConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        paramaters = parse_qs(self.scope['query_string'].decode('utf8'))
        uuid = paramaters['uuid']
        
        
        if(not is_authorized(uuid,'volunteers')):
            return
        
        self.room_group_name = 'select_refresh'

        
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        raise StopConsumer 
    

    # Receive message from room group
    async def select_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
    