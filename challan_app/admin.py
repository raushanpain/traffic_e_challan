from django.contrib import admin
from .models import Vehicle, ViolationType, Challan, ViolationEvidence, Payment, PoliceOfficer

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'vehicle_type', 'owner_name', 'owner_phone', 'created_at']
    list_filter = ['vehicle_type', 'created_at']
    search_fields = ['registration_number', 'owner_name', 'owner_phone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(ViolationType)
class ViolationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'fine_amount', 'penalty_points', 'is_active']
    list_filter = ['is_active', 'penalty_points']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at']
    ordering = ['name']

@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    list_display = ['challan_number', 'vehicle', 'violation_type', 'fine_amount', 'status', 'issued_by', 'issued_at']
    list_filter = ['status', 'violation_type', 'issued_at']
    search_fields = ['challan_number', 'vehicle__registration_number', 'vehicle__owner_name']
    readonly_fields = ['id', 'challan_number', 'issued_at']
    ordering = ['-issued_at']
    date_hierarchy = 'issued_at'

@admin.register(ViolationEvidence)
class ViolationEvidenceAdmin(admin.ModelAdmin):
    list_display = ['challan', 'evidence_type', 'file_size', 'is_processed', 'uploaded_at']
    list_filter = ['evidence_type', 'is_processed', 'uploaded_at']
    search_fields = ['challan__challan_number']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['-uploaded_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'challan', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['transaction_id', 'challan__challan_number']
    readonly_fields = ['id', 'payment_date']
    ordering = ['-payment_date']

@admin.register(PoliceOfficer)
class PoliceOfficerAdmin(admin.ModelAdmin):
    list_display = ['badge_number', 'user', 'rank', 'station', 'is_active']
    list_filter = ['rank', 'station', 'is_active']
    search_fields = ['badge_number', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at']
    ordering = ['badge_number']
