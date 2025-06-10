from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# Main router
router = DefaultRouter()
router.register(r'meetings', views.MeetingViewSet, basename='meeting')
router.register(r'recordings', views.MeetingRecordingViewSet, basename='recording')
router.register(r'invitations', views.MeetingInvitationViewSet, basename='invitation')
router.register(r'settings', views.MeetingSettingsViewSet, basename='settings')

# Nested routers for meeting-specific resources
meetings_router = routers.NestedDefaultRouter(router, r'meetings', lookup='meeting')
meetings_router.register(r'participants', views.MeetingParticipantViewSet, basename='meeting-participants')
meetings_router.register(r'chat', views.MeetingChatViewSet, basename='meeting-chat')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(meetings_router.urls)),
]