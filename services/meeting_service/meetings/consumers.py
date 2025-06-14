import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from .models import Meeting, MeetingParticipant

logger = logging.getLogger(__name__)


class MeetingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time meeting communication
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.room_group_name = f'meeting_{self.meeting_id}'
        self.participant_id = None

        # Validate meeting exists
        meeting = await self.get_meeting(self.meeting_id)
        if not meeting:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connected to meeting {self.meeting_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Update participant status if they were connected
        if self.participant_id:
            await self.update_participant_connection_status(self.participant_id, False)

        logger.info(f"WebSocket disconnected from meeting {self.meeting_id}")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'join_room':
                await self.handle_join_room(data)
            elif message_type == 'webrtc_offer':
                await self.handle_webrtc_offer(data)
            elif message_type == 'webrtc_answer':
                await self.handle_webrtc_answer(data)
            elif message_type == 'ice_candidate':
                await self.handle_ice_candidate(data)
            elif message_type == 'media_control':
                await self.handle_media_control(data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'screen_share':
                await self.handle_screen_share(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def handle_join_room(self, data):
        """Handle participant joining the room"""
        self.participant_id = data.get('participant_id')
        participant_name = data.get('participant_name', 'Unknown')

        # Update participant connection status
        await self.update_participant_connection_status(self.participant_id, True)

        # Notify other participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'participant_joined',
                'participant_id': self.participant_id,
                'participant_name': participant_name,
                'meeting_id': self.meeting_id
            }
        )

    async def handle_webrtc_offer(self, data):
        """Handle WebRTC offer"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_offer',
                'offer': data.get('offer'),
                'from_participant': data.get('from_participant'),
                'to_participant': data.get('to_participant'),
                'meeting_id': self.meeting_id
            }
        )

    async def handle_webrtc_answer(self, data):
        """Handle WebRTC answer"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_answer',
                'answer': data.get('answer'),
                'from_participant': data.get('from_participant'),
                'to_participant': data.get('to_participant'),
                'meeting_id': self.meeting_id
            }
        )

    async def handle_ice_candidate(self, data):
        """Handle ICE candidate"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ice_candidate',
                'candidate': data.get('candidate'),
                'from_participant': data.get('from_participant'),
                'to_participant': data.get('to_participant'),
                'meeting_id': self.meeting_id
            }
        )

    async def handle_media_control(self, data):
        """Handle media control (mute/unmute, video on/off)"""
        control_type = data.get('control_type')
        participant_id = data.get('participant_id')
        enabled = data.get('enabled', False)

        # Update participant media status
        await self.update_participant_media_status(participant_id, control_type, enabled)

        # Notify other participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'media_control',
                'control_type': control_type,
                'participant_id': participant_id,
                'enabled': enabled,
                'meeting_id': self.meeting_id
            }
        )

    async def handle_chat_message(self, data):
        """Handle chat messages"""
        message = data.get('message')
        participant_id = data.get('participant_id')
        participant_name = data.get('participant_name')
        timestamp = data.get('timestamp')

        # Save chat message (you might want to create a ChatMessage model)
        # await self.save_chat_message(message, participant_id)

        # Broadcast to all participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'participant_id': participant_id,
                'participant_name': participant_name,
                'timestamp': timestamp,
                'meeting_id': self.meeting_id
            }
        )

    async def handle_screen_share(self, data):
        """Handle screen sharing"""
        action = data.get('action')  # 'start' or 'stop'
        participant_id = data.get('participant_id')

        # Update participant screen sharing status
        await self.update_participant_screen_sharing(participant_id, action == 'start')

        # Notify other participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'screen_share',
                'action': action,
                'participant_id': participant_id,
                'meeting_id': self.meeting_id
            }
        )

    # Group message handlers
    async def participant_joined(self, event):
        """Send participant joined message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'participant_joined',
            'participant_id': event['participant_id'],
            'participant_name': event['participant_name'],
            'meeting_id': event['meeting_id']
        }))

    async def participant_left(self, event):
        """Send participant left message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'participant_left',
            'participant_id': event['participant_id'],
            'meeting_id': event['meeting_id']
        }))

    async def webrtc_offer(self, event):
        """Send WebRTC offer to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'webrtc_offer',
            'offer': event['offer'],
            'from_participant': event['from_participant'],
            'to_participant': event['to_participant'],
            'meeting_id': event['meeting_id']
        }))

    async def webrtc_answer(self, event):
        """Send WebRTC answer to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'webrtc_answer',
            'answer': event['answer'],
            'from_participant': event['from_participant'],
            'to_participant': event['to_participant'],
            'meeting_id': event['meeting_id']
        }))

    async def ice_candidate(self, event):
        """Send ICE candidate to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'from_participant': event['from_participant'],
            'to_participant': event['to_participant'],
            'meeting_id': event['meeting_id']
        }))

    async def media_control(self, event):
        """Send media control message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'media_control',
            'control_type': event['control_type'],
            'participant_id': event['participant_id'],
            'enabled': event['enabled'],
            'meeting_id': event['meeting_id']
        }))

    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'participant_id': event['participant_id'],
            'participant_name': event['participant_name'],
            'timestamp': event['timestamp'],
            'meeting_id': event['meeting_id']
        }))

    async def screen_share(self, event):
        """Send screen share message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'screen_share',
            'action': event['action'],
            'participant_id': event['participant_id'],
            'meeting_id': event['meeting_id']
        }))

    async def meeting_status_change(self, event):
        """Send meeting status change to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'meeting_status_change',
            'meeting_id': event['meeting_id'],
            'action': event['action'],
            'timestamp': event['timestamp']
        }))

    async def webrtc_signaling(self, event):
        """Send WebRTC signaling message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'webrtc_signaling',
            'signaling_data': event['signaling_data'],
            'meeting_id': event['meeting_id']
        }))

    async def meeting_control(self, event):
        """Send meeting control message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'meeting_control',
            'action': event['action'],
            'participant_id': event['participant_id'],
            'target_participant_id': event.get('target_participant_id'),
            'meeting_id': event['meeting_id']
        }))

    # Database operations
    @database_sync_to_async
    def get_meeting(self, meeting_id):
        """Get meeting from database"""
        try:
            return Meeting.objects.get(meeting_id=meeting_id)
        except Meeting.DoesNotExist:
            return None

    @database_sync_to_async
    def update_participant_connection_status(self, participant_id, connected):
        """Update participant connection status"""
        try:
            participant = MeetingParticipant.objects.get(id=participant_id)
            if connected:
                participant.socket_id = self.channel_name
            else:
                participant.socket_id = None
            participant.save()
        except MeetingParticipant.DoesNotExist:
            logger.error(f"Participant {participant_id} not found")

    @database_sync_to_async
    def update_participant_media_status(self, participant_id, control_type, enabled):
        """Update participant media status"""
        try:
            participant = MeetingParticipant.objects.get(id=participant_id)
            if control_type == 'audio':
                participant.audio_enabled = enabled
            elif control_type == 'video':
                participant.video_enabled = enabled
            participant.save()
        except MeetingParticipant.DoesNotExist:
            logger.error(f"Participant {participant_id} not found")

    @database_sync_to_async
    def update_participant_screen_sharing(self, participant_id, sharing):
        """Update participant screen sharing status"""
        try:
            participant = MeetingParticipant.objects.get(id=participant_id)
            participant.screen_sharing = sharing
            participant.save()
        except MeetingParticipant.DoesNotExist:
            logger.error(f"Participant {participant_id} not found")