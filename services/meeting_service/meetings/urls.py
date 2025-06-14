from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'meetings', views.MeetingViewSet, basename='meeting')

app_name = 'meetings'

urlpatterns = [
    # ViewSet URLs (CRUD operations for meetings)
    path('api/', include(router.urls)),

    # Public meeting info (no authentication required)
    path('api/meetings/<str:meeting_id>/info/', views.PublicMeetingView.as_view(), name='public-meeting-info'),

    # Join meeting
    path('api/meetings/<str:meeting_id>/join/', views.JoinMeetingView.as_view(), name='join-meeting'),

    # Leave meeting
    path('api/meetings/<str:meeting_id>/participants/<uuid:participant_id>/leave/',
         views.LeaveMeetingView.as_view(), name='leave-meeting'),

    # WebRTC signaling
    path('api/meetings/<str:meeting_id>/signaling/', views.WebRTCSignalingView.as_view(), name='webrtc-signaling'),

    # Meeting controls (mute, video, screen share, etc.)
    path('api/meetings/<str:meeting_id>/controls/', views.MeetingControlView.as_view(), name='meeting-controls'),

    # Meeting statistics
    path('api/meetings/<str:meeting_id>/stats/', views.MeetingStatsView.as_view(), name='meeting-stats'),
]