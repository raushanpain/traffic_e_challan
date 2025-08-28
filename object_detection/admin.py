from django.contrib import admin
from .models import DetectionSession, VideoSource, DetectionResult, ROI, ModelConfiguration

@admin.register(DetectionSession)
class DetectionSessionAdmin(admin.ModelAdmin):
    list_display = ['session_name', 'user', 'status', 'started_at', 'total_frames_processed', 'total_detections']
    list_filter = ['status', 'started_at']
    search_fields = ['session_name', 'user__username']
    readonly_fields = ['id', 'started_at', 'total_frames_processed', 'total_detections']
    ordering = ['-started_at']
    date_hierarchy = 'started_at'

@admin.register(VideoSource)
class VideoSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'is_active', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name', 'source_url', 'file_path']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ['session', 'video_source', 'frame_number', 'timestamp', 'processing_time']
    list_filter = ['session', 'video_source', 'timestamp']
    search_fields = ['session__session_name', 'video_source__name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

@admin.register(ROI)
class ROIAdmin(admin.ModelAdmin):
    list_display = ['name', 'video_source', 'x_coordinate', 'y_coordinate', 'width', 'height', 'is_active']
    list_filter = ['video_source', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']

@admin.register(ModelConfiguration)
class ModelConfigurationAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'confidence_threshold', 'nms_threshold', 'max_detections', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['model_name', 'model_path']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['model_name']
