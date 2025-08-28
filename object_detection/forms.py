from django import forms
from .models import VideoSource, ROI, ModelConfiguration, DetectionSession

class VideoSourceForm(forms.ModelForm):
    """Form for creating and editing video sources"""
    
    class Meta:
        model = VideoSource
        fields = [
            'name',
            'source_type',
            'source_url',
            'file_path',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter source name'
            }),
            'source_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'source_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter camera URL or stream URL'
            }),
            'file_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter file path (for file sources)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        source_type = cleaned_data.get('source_type')
        source_url = cleaned_data.get('source_url')
        file_path = cleaned_data.get('file_path')
        
        if source_type == 'CAMERA' and not source_url:
            raise forms.ValidationError("Camera URL is required for camera sources")
        
        if source_type == 'FILE' and not file_path:
            raise forms.ValidationError("File path is required for file sources")
        
        return cleaned_data

class ROIForm(forms.ModelForm):
    """Form for creating and editing ROIs"""
    
    class Meta:
        model = ROI
        fields = [
            'name',
            'x_coordinate',
            'y_coordinate',
            'width',
            'height',
            'description',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ROI name'
            }),
            'x_coordinate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'X coordinate'
            }),
            'y_coordinate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Y coordinate'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Width'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Height'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description of this ROI'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        x = cleaned_data.get('x_coordinate')
        y = cleaned_data.get('y_coordinate')
        width = cleaned_data.get('width')
        height = cleaned_data.get('height')
        
        if x is not None and x < 0:
            raise forms.ValidationError("X coordinate cannot be negative")
        
        if y is not None and y < 0:
            raise forms.ValidationError("Y coordinate cannot be negative")
        
        if width is not None and width <= 0:
            raise forms.ValidationError("Width must be positive")
        
        if height is not None and height <= 0:
            raise forms.ValidationError("Height must be positive")
        
        return cleaned_data

class ModelConfigurationForm(forms.ModelForm):
    """Form for creating and editing model configurations"""
    
    class Meta:
        model = ModelConfiguration
        fields = [
            'model_name',
            'model_path',
            'labels_path',
            'confidence_threshold',
            'nms_threshold',
            'max_detections',
            'is_active',
        ]
        widgets = {
            'model_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter model name'
            }),
            'model_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter path to model file'
            }),
            'labels_path': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter path to labels file'
            }),
            'confidence_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.0',
                'max': '1.0',
                'placeholder': '0.5'
            }),
            'nms_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.0',
                'max': '1.0',
                'placeholder': '0.4'
            }),
            'max_detections': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': '100'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_confidence_threshold(self):
        threshold = self.cleaned_data['confidence_threshold']
        if threshold < 0.0 or threshold > 1.0:
            raise forms.ValidationError("Confidence threshold must be between 0.0 and 1.0")
        return threshold
    
    def clean_nms_threshold(self):
        threshold = self.cleaned_data['nms_threshold']
        if threshold < 0.0 or threshold > 1.0:
            raise forms.ValidationError("NMS threshold must be between 0.0 and 1.0")
        return threshold
    
    def clean_max_detections(self):
        max_det = self.cleaned_data['max_detections']
        if max_det < 1:
            raise forms.ValidationError("Maximum detections must be at least 1")
        return max_det

class DetectionSessionForm(forms.ModelForm):
    """Form for creating detection sessions"""
    
    class Meta:
        model = DetectionSession
        fields = [
            'session_name',
            'processing_notes',
        ]
        widgets = {
            'session_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter session name'
            }),
            'processing_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this detection session'
            }),
        }

class VideoUploadForm(forms.Form):
    """Form for uploading video files"""
    video_file = forms.FileField(
        label='Select Video File',
        help_text='Supported formats: MP4, AVI, MOV, MKV (Max size: 100MB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*'
        })
    )
    
    source_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional: Custom name for this video source'
        })
    )
    
    def clean_video_file(self):
        video_file = self.cleaned_data['video_file']
        
        # Check file size (100MB limit)
        if video_file.size > 100 * 1024 * 1024:
            raise forms.ValidationError("Video file size must be less than 100MB")
        
        # Check file extension
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        file_extension = video_file.name.lower()
        
        if not any(file_extension.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        return video_file
