import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Meeting, MeetingParticipant, MeetingChat

User = get_user_model()

class MeetingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.meeting_group_name = f'meeting_{self.meeting_id}'

        # Join meeting group
        await self.channel_layer.group_add(
            self.meeting_group_name,
            self.channel_name
        )

        await self.accept()

        # Update participant status
        await self.update_participant_status('joined')

    async def disconnect(self, close_code):
        # Leave meeting group
        await self.channel_layer.group_discard(
            self.meeting_group_name,
            self.channel_name
        )

        # Update participant status
        await self.update_participant_status('left')

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'participant_update':
            await self.handle_participant_update(data)
        elif message_type == 'screen_share':
            await self.handle_screen_share(data)

    async def handle_chat_message(self, data):
        # Save chat message to database
        await self.save_chat_message(data['message'])

        # Broadcast to meeting group
        await self.channel_layer.group_send(
            self.meeting_group_name,
            {
                'type': 'chat_message',
                'message': data['message'],
                'user': self.scope['user'].full_name,
                'timestamp': data.get('timestamp')
            }
        )

    async def chat_message(self, event):
        # Send chat message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user': event['user'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_chat_message(self, message):
        # Implementation to save chat message
        pass

    @database_sync_to_async
    def update_participant_status(self, status):
        # Implementation to update participant status
        pass