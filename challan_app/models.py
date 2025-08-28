from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Vehicle(models.Model):
    """Model for storing vehicle information"""
    VEHICLE_TYPES = [
        ('2W', 'Two Wheeler'),
        ('4W', 'Four Wheeler'),
        ('CV', 'Commercial Vehicle'),
        ('HV', 'Heavy Vehicle'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=2, choices=VEHICLE_TYPES)
    owner_name = models.CharField(max_length=100)
    owner_phone = models.CharField(max_length=15)
    owner_email = models.EmailField(blank=True, null=True)
    owner_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.registration_number} - {self.owner_name}"
    
    class Meta:
        db_table = 'vehicles'
        app_label = 'challan_app'

class ViolationType(models.Model):
    """Model for storing different types of traffic violations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    penalty_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - ₹{self.fine_amount}"
    
    class Meta:
        db_table = 'violation_types'
        app_label = 'challan_app'

class Challan(models.Model):
    """Model for storing challan information"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('DISPUTED', 'Disputed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challan_number = models.CharField(max_length=20, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    violation_type = models.ForeignKey(ViolationType, on_delete=models.CASCADE)
    violation_date = models.DateTimeField()
    violation_location = models.CharField(max_length=200)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    penalty_points = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Challan {self.challan_number} - {self.vehicle.registration_number}"
    
    def save(self, *args, **kwargs):
        if not self.challan_number:
            # Generate challan number
            year = timezone.now().year
            count = Challan.objects.filter(issued_at__year=year).count() + 1
            self.challan_number = f"CH{year}{count:06d}"
        
        if not self.fine_amount:
            self.fine_amount = self.violation_type.fine_amount
        
        if not self.penalty_points:
            self.penalty_points = self.violation_type.penalty_points
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'challans'
        app_label = 'challan_app'

class ViolationEvidence(models.Model):
    """Model for storing evidence of violations (images, videos)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challan = models.ForeignKey(Challan, on_delete=models.CASCADE, related_name='evidence')
    evidence_type = models.CharField(max_length=20, choices=[
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('DOCUMENT', 'Document'),
    ])
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()  # in bytes
    mime_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    processing_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Evidence for {self.challan.challan_number}"
    
    class Meta:
        db_table = 'violation_evidence'
        app_label = 'challan_app'

class Payment(models.Model):
    """Model for storing payment information"""
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('NETBANKING', 'Net Banking'),
        ('WALLET', 'Digital Wallet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challan = models.OneToOneField(Challan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ], default='PENDING')
    gateway_response = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment {self.transaction_id} - ₹{self.amount}"
    
    class Meta:
        db_table = 'payments'
        app_label = 'challan_app'

class PoliceOfficer(models.Model):
    """Model for storing police officer information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    badge_number = models.CharField(max_length=20, unique=True)
    rank = models.CharField(max_length=50)
    station = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.rank} {self.user.get_full_name()} - {self.badge_number}"
    
    class Meta:
        db_table = 'police_officers'
        app_label = 'challan_app'
