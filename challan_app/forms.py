from django import forms
from django.utils import timezone
from .models import Vehicle, ViolationType, Challan, ViolationEvidence

class VehicleForm(forms.ModelForm):
    """Form for creating and editing vehicles"""
    
    class Meta:
        model = Vehicle
        fields = [
            'registration_number',
            'vehicle_type',
            'owner_name',
            'owner_phone',
            'owner_email',
            'owner_address',
        ]
        widgets = {
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter vehicle registration number'
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'owner_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter owner name'
            }),
            'owner_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'owner_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'owner_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter complete address'
            }),
        }
    
    def clean_registration_number(self):
        """Validate registration number format"""
        reg_number = self.cleaned_data['registration_number']
        # Add custom validation logic here
        return reg_number.upper()
    
    def clean_owner_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data['owner_phone']
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits")
        return phone

class ChallanForm(forms.ModelForm):
    """Form for creating and editing challans"""
    
    class Meta:
        model = Challan
        fields = [
            'vehicle',
            'violation_type',
            'violation_date',
            'violation_location',
            'fine_amount',
            'penalty_points',
            'notes',
        ]
        widgets = {
            'vehicle': forms.Select(attrs={
                'class': 'form-control',
                'data-placeholder': 'Select vehicle'
            }),
            'violation_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'violation_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'violation_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter violation location'
            }),
            'fine_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'penalty_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about the violation'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default violation date to current time
        if not self.instance.pk:
            self.fields['violation_date'].initial = timezone.now()
        
        # Auto-fill fine amount and penalty points based on violation type
        if 'violation_type' in self.fields:
            self.fields['violation_type'].widget.attrs.update({
                'onchange': 'updateFineAndPoints(this.value)'
            })
    
    def clean_violation_date(self):
        """Validate violation date"""
        violation_date = self.cleaned_data['violation_date']
        if violation_date > timezone.now():
            raise forms.ValidationError("Violation date cannot be in the future")
        return violation_date
    
    def clean_fine_amount(self):
        """Validate fine amount"""
        fine_amount = self.cleaned_data['fine_amount']
        if fine_amount <= 0:
            raise forms.ValidationError("Fine amount must be greater than zero")
        return fine_amount

class ViolationEvidenceForm(forms.ModelForm):
    """Form for uploading violation evidence"""
    
    class Meta:
        model = ViolationEvidence
        fields = [
            'evidence_type',
            'file_path',
            'mime_type',
        ]
        widgets = {
            'evidence_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file_path': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*,.pdf,.doc,.docx'
            }),
            'mime_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., image/jpeg, video/mp4'
            }),
        }
    
    def clean_file_path(self):
        """Validate uploaded file"""
        file_path = self.cleaned_data['file_path']
        if file_path:
            # Add file validation logic here
            # Check file size, type, etc.
            pass
        return file_path

class VehicleSearchForm(forms.Form):
    """Form for searching vehicles"""
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by registration number or owner name...'
        })
    )
    
    vehicle_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Vehicle.VEHICLE_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

class ChallanFilterForm(forms.Form):
    """Form for filtering challans"""
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Challan.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    violation_type = forms.ModelChoiceField(
        queryset=ViolationType.objects.filter(is_active=True),
        required=False,
        empty_label="All Violation Types",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
