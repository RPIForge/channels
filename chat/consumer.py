# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import UserQueue
from chat.models import ChatLog
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    
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

            
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    
    #### RECEIVE HELPER ####
    @database_sync_to_async
    def delete_room(self):
        return UserQueue.objects.filter(room_id=self.room_name).delete()
    
    @database_sync_to_async
    def add_text(self,string_data):
        room = UserQueue.objects.get(room_id=self.room_name)
        log = ChatLog.objects.get(id=room.log_id)
        log.text = log.text + string_data
        return log.save()
    
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        if("volunteer_finish" in text_data_json):
            await self.delete_room()
        elif("volunteer_info" in text_data_json):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'volunteer_info': text_data_json["volunteer_info"]
                }
            )
        elif("message" in text_data_json):
            message = text_data_json['message']
            
            await self.add_text(str(message+'\n'))
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))