from django.db import models
from django.contrib.auth.models import User
import uuid

class DetectionSession(models.Model):
    """Model for storing object detection sessions"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('ERROR', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    total_frames_processed = models.IntegerField(default=0)
    total_detections = models.IntegerField(default=0)
    processing_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Session {self.session_name} - {self.user.username}"
    
    class Meta:
        db_table = 'detection_sessions'
        app_label = 'object_detection'

class VideoSource(models.Model):
    """Model for storing video sources (cameras, uploaded files)"""
    SOURCE_TYPES = [
        ('CAMERA', 'Live Camera'),
        ('FILE', 'Video File'),
        ('STREAM', 'Video Stream'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    source_url = models.CharField(max_length=500, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.source_type}"
    
    class Meta:
        db_table = 'video_sources'
        app_label = 'object_detection'

class DetectionResult(models.Model):
    """Model for storing object detection results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DetectionSession, on_delete=models.CASCADE)
    video_source = models.ForeignKey(VideoSource, on_delete=models.CASCADE)
    frame_number = models.IntegerField()
    timestamp = models.DateTimeField()
    detected_objects = models.JSONField()  # Store detection results as JSON
    confidence_scores = models.JSONField()  # Store confidence scores
    bounding_boxes = models.JSONField()  # Store bounding box coordinates
    processing_time = models.FloatField()  # Time taken to process this frame
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Detection {self.id} - Frame {self.frame_number}"
    
    class Meta:
        db_table = 'detection_results'
        app_label = 'object_detection'

class ROI(models.Model):
    """Model for storing Region of Interest (ROI) definitions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    video_source = models.ForeignKey(VideoSource, on_delete=models.CASCADE)
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"ROI {self.name} - ({self.x_coordinate}, {self.y_coordinate})"
    
    class Meta:
        db_table = 'rois'
        app_label = 'object_detection'

class ModelConfiguration(models.Model):
    """Model for storing object detection model configurations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=100)
    model_path = models.CharField(max_length=500)
    labels_path = models.CharField(max_length=500)
    confidence_threshold = models.FloatField(default=0.5)
    nms_threshold = models.FloatField(default=0.4)
    max_detections = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Model {self.model_name}"
    
    class Meta:
        db_table = 'model_configurations'
        app_label = 'object_detection'
