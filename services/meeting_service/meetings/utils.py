import random
import string
import secrets
from django.conf import settings


def get_ice_servers():
    """
    Get ICE servers configuration for WebRTC
    """
    # Default STUN servers
    ice_servers = [
        {
            'urls': [
                'stun:stun.l.google.com:19302',
                'stun:stun1.l.google.com:19302',
                'stun:stun2.l.google.com:19302',
            ]
        }
    ]

    # Add TURN servers if configured
    if hasattr(settings, 'TURN_SERVERS') and settings.TURN_SERVERS:
        for turn_server in settings.TURN_SERVERS:
            ice_servers.append({
                'urls': turn_server['urls'],
                'username': turn_server.get('username'),
                'credential': turn_server.get('credential')
            })

    return ice_servers


def generate_peer_id():
    """
    Generate unique peer ID for WebRTC connections
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def generate_room_id():
    """
    Generate unique room ID for WebRTC room
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))


def generate_meeting_token():
    """
    Generate secure meeting token
    """
    return secrets.token_urlsafe(32)


def validate_meeting_passcode(passcode):
    """
    Validate meeting passcode format
    """
    if not passcode:
        return True

    if len(passcode) < 4 or len(passcode) > 10:
        return False

    return passcode.isdigit()


def format_duration(seconds):
    """
    Format duration in seconds to human readable format
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def get_client_timezone(request):
    """
    Get client timezone from request headers
    """
    return request.META.get('HTTP_X_TIMEZONE', 'UTC')


def is_meeting_host(meeting, user):
    """
    Check if user is the meeting host
    """
    if not user or not user.is_authenticated:
        return False
    return str(meeting.host_id) == str(user.id)