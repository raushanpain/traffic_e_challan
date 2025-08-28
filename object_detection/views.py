from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
import os
import cv2
import numpy as np
import json
import uuid
from datetime import datetime
from django.db import models

from .models import DetectionSession, VideoSource, DetectionResult, ROI, ModelConfiguration
from .forms import VideoSourceForm, ROIForm
from .utils.object_detector import ObjectDetector

@login_required
def detection_dashboard(request):
    """Main dashboard for object detection"""
    active_sessions = DetectionSession.objects.filter(status='ACTIVE').count()
    total_sources = VideoSource.objects.filter(is_active=True).count()
    recent_detections = DetectionResult.objects.select_related('session', 'video_source').order_by('-timestamp')[:10]
    
    context = {
        'active_sessions': active_sessions,
        'total_sources': total_sources,
        'recent_detections': recent_detections,
    }
    
    return render(request, 'object_detection/dashboard.html', context)

@login_required
def video_sources(request):
    """List and manage video sources"""
    sources = VideoSource.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = VideoSourceForm(request.POST)
        if form.is_valid():
            source = form.save()
            messages.success(request, f'Video source "{source.name}" created successfully.')
            return redirect('video_sources')
    else:
        form = VideoSourceForm()
    
    context = {
        'sources': sources,
        'form': form,
    }
    
    return render(request, 'object_detection/video_sources.html', context)

@login_required
def video_source_detail(request, source_id):
    """Show video source details and associated ROIs"""
    source = get_object_or_404(VideoSource, id=source_id)
    rois = ROI.objects.filter(video_source=source, is_active=True)
    recent_detections = DetectionResult.objects.filter(video_source=source).order_by('-timestamp')[:20]
    
    context = {
        'source': source,
        'rois': rois,
        'recent_detections': recent_detections,
    }
    
    return render(request, 'object_detection/video_source_detail.html', context)

@login_required
def start_detection(request, source_id):
    """Start object detection on a video source"""
    source = get_object_or_404(VideoSource, id=source_id)
    
    if request.method == 'POST':
        # Create new detection session
        session = DetectionSession.objects.create(
            session_name=f"Detection on {source.name}",
            user=request.user,
            status='ACTIVE'
        )
        
        # Start detection in background
        try:
            detector = ObjectDetector()
            detector.start_detection(session, source)
            messages.success(request, f'Detection started on {source.name}')
        except Exception as e:
            session.status = 'ERROR'
            session.processing_notes = str(e)
            session.save()
            messages.error(request, f'Failed to start detection: {str(e)}')
        
        return redirect('detection_sessions')
    
    context = {
        'source': source,
    }
    
    return render(request, 'object_detection/start_detection.html', context)

@login_required
def detection_sessions(request):
    """List all detection sessions"""
    sessions = DetectionSession.objects.select_related('user').order_by('-started_at')
    
    context = {
        'sessions': sessions,
    }
    
    return render(request, 'object_detection/detection_sessions.html', context)

@login_required
def session_detail(request, session_id):
    """Show detection session details and results"""
    session = get_object_or_404(DetectionSession, id=session_id)
    results = DetectionResult.objects.filter(session=session).order_by('-timestamp')
    
    # Get detection statistics
    total_frames = results.count()
    avg_processing_time = results.aggregate(avg_time=models.Avg('processing_time'))['avg_time'] or 0
    
    context = {
        'session': session,
        'results': results,
        'total_frames': total_frames,
        'avg_processing_time': avg_processing_time,
    }
    
    return render(request, 'object_detection/session_detail.html', context)

@login_required
def manage_rois(request, source_id):
    """Manage ROIs for a video source"""
    source = get_object_or_404(VideoSource, id=source_id)
    rois = ROI.objects.filter(video_source=source)
    
    if request.method == 'POST':
        form = ROIForm(request.POST)
        if form.is_valid():
            roi = form.save(commit=False)
            roi.video_source = source
            roi.save()
            messages.success(request, f'ROI "{roi.name}" created successfully.')
            return redirect('manage_rois', source_id=source_id)
    else:
        form = ROIForm()
    
    context = {
        'source': source,
        'rois': rois,
        'form': form,
    }
    
    return render(request, 'object_detection/manage_rois.html', context)

@login_required
def roi_edit(request, roi_id):
    """Edit an existing ROI"""
    roi = get_object_or_404(ROI, id=roi_id)
    
    if request.method == 'POST':
        form = ROIForm(request.POST, instance=roi)
        if form.is_valid():
            form.save()
            messages.success(request, f'ROI "{roi.name}" updated successfully.')
            return redirect('manage_rois', source_id=roi.video_source.id)
    else:
        form = ROIForm(instance=roi)
    
    context = {
        'form': form,
        'roi': roi,
        'title': f'Edit ROI {roi.name}',
    }
    
    return render(request, 'object_detection/roi_form.html', context)

@login_required
def roi_delete(request, roi_id):
    """Delete an ROI"""
    roi = get_object_or_404(ROI, id=roi_id)
    source_id = roi.video_source.id
    
    if request.method == 'POST':
        roi.delete()
        messages.success(request, f'ROI "{roi.name}" deleted successfully.')
        return redirect('manage_rois', source_id=source_id)
    
    context = {
        'roi': roi,
    }
    
    return render(request, 'object_detection/roi_confirm_delete.html', context)

@login_required
def upload_video(request):
    """Upload video file for processing"""
    if request.method == 'POST':
        video_file = request.FILES.get('video_file')
        if video_file:
            # Generate unique filename
            file_extension = os.path.splitext(video_file.name)[1]
            filename = f"videos/{uuid.uuid4()}{file_extension}"
            
            # Save file
            file_path = default_storage.save(filename, video_file)
            
            # Create video source
            source = VideoSource.objects.create(
                name=f"Uploaded: {video_file.name}",
                source_type='FILE',
                file_path=file_path,
                is_active=True
            )
            
            messages.success(request, f'Video "{video_file.name}" uploaded successfully.')
            return redirect('video_source_detail', source_id=source.id)
        else:
            messages.error(request, 'Please select a video file.')
    
    return render(request, 'object_detection/upload_video.html')

@login_required
def live_detection(request):
    """Live object detection interface"""
    sources = VideoSource.objects.filter(source_type='CAMERA', is_active=True)
    
    context = {
        'sources': sources,
    }
    
    return render(request, 'object_detection/live_detection.html', context)

@login_required
def api_detection_results(request, session_id):
    """API endpoint for getting detection results"""
    session = get_object_or_404(DetectionSession, id=session_id)
    results = DetectionResult.objects.filter(session=session).order_by('-timestamp')[:100]
    
    data = [{
        'id': str(result.id),
        'frame_number': result.frame_number,
        'timestamp': result.timestamp.isoformat(),
        'detected_objects': result.detected_objects,
        'confidence_scores': result.confidence_scores,
        'bounding_boxes': result.bounding_boxes,
        'processing_time': result.processing_time,
    } for result in results]
    
    return JsonResponse({'results': data})

@login_required
def api_start_detection(request):
    """API endpoint for starting detection"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            source_id = data.get('source_id')
            session_name = data.get('session_name', 'API Detection')
            
            source = get_object_or_404(VideoSource, id=source_id)
            
            # Create session
            session = DetectionSession.objects.create(
                session_name=session_name,
                user=request.user,
                status='ACTIVE'
            )
            
            # Start detection
            detector = ObjectDetector()
            detector.start_detection(session, source)
            
            return JsonResponse({
                'success': True,
                'session_id': str(session.id),
                'message': 'Detection started successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def api_stop_detection(request, session_id):
    """API endpoint for stopping detection"""
    if request.method == 'POST':
        session = get_object_or_404(DetectionSession, id=session_id)
        session.status = 'COMPLETED'
        session.ended_at = timezone.now()
        session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Detection stopped successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def video_stream(request, source_id):
    """Stream video for live viewing"""
    source = get_object_or_404(VideoSource, id=source_id)
    
    def generate_frames():
        if source.source_type == 'CAMERA':
            cap = cv2.VideoCapture(source.source_url)
        elif source.source_type == 'FILE':
            cap = cv2.VideoCapture(source.file_path)
        else:
            return
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Encode frame
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
        finally:
            cap.release()
    
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
