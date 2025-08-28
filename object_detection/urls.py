from django.urls import path
from . import views

app_name = 'object_detection'

urlpatterns = [
    # Dashboard
    path('', views.detection_dashboard, name='dashboard'),
    
    # Video sources
    path('sources/', views.video_sources, name='video_sources'),
    path('sources/<uuid:source_id>/', views.video_source_detail, name='video_source_detail'),
    path('sources/<uuid:source_id>/start/', views.start_detection, name='start_detection'),
    path('sources/<uuid:source_id>/rois/', views.manage_rois, name='manage_rois'),
    
    # ROIs
    path('rois/<uuid:roi_id>/edit/', views.roi_edit, name='roi_edit'),
    path('rois/<uuid:roi_id>/delete/', views.roi_delete, name='roi_delete'),
    
    # Detection sessions
    path('sessions/', views.detection_sessions, name='detection_sessions'),
    path('sessions/<uuid:session_id>/', views.session_detail, name='session_detail'),
    
    # Video upload
    path('upload/', views.upload_video, name='upload_video'),
    
    # Live detection
    path('live/', views.live_detection, name='live_detection'),
    
    # Video streaming
    path('stream/<uuid:source_id>/', views.video_stream, name='video_stream'),
    
    # API endpoints
    path('api/sessions/<uuid:session_id>/results/', views.api_detection_results, name='api_detection_results'),
    path('api/start-detection/', views.api_start_detection, name='api_start_detection'),
    path('api/sessions/<uuid:session_id>/stop/', views.api_stop_detection, name='api_stop_detection'),
]
