from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Vehicle, ViolationType, Challan, ViolationEvidence, Payment, PoliceOfficer
from .forms import VehicleForm, ChallanForm, ViolationEvidenceForm

@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get statistics
    total_vehicles = Vehicle.objects.count()
    total_challans = Challan.objects.count()
    pending_challans = Challan.objects.filter(status='PENDING').count()
    paid_challans = Challan.objects.filter(status='PAID').count()
    
    # Get recent challans
    recent_challans = Challan.objects.select_related('vehicle', 'violation_type').order_by('-issued_at')[:10]
    
    # Get monthly statistics
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_challans = Challan.objects.filter(
        issued_at__year=current_year,
        issued_at__month=current_month
    ).count()
    
    monthly_revenue = Challan.objects.filter(
        issued_at__year=current_year,
        issued_at__month=current_month,
        status='PAID'
    ).aggregate(total=Sum('fine_amount'))['total'] or 0
    
    context = {
        'total_vehicles': total_vehicles,
        'total_challans': total_challans,
        'pending_challans': pending_challans,
        'paid_challans': paid_challans,
        'monthly_challans': monthly_challans,
        'monthly_revenue': monthly_revenue,
        'recent_challans': recent_challans,
    }
    
    return render(request, 'challan_app/dashboard.html', context)

@login_required
def vehicle_list(request):
    """List all vehicles"""
    vehicles = Vehicle.objects.all().order_by('-created_at')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        vehicles = vehicles.filter(
            Q(registration_number__icontains=query) |
            Q(owner_name__icontains=query) |
            Q(owner_phone__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(vehicles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    
    return render(request, 'challan_app/vehicle_list.html', context)

@login_required
def vehicle_detail(request, vehicle_id):
    """Show vehicle details and challan history"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    challans = Challan.objects.filter(vehicle=vehicle).order_by('-issued_at')
    
    # Calculate total fines and points
    total_fines = challans.filter(status='PAID').aggregate(total=Sum('fine_amount'))['total'] or 0
    total_points = challans.aggregate(total=Sum('penalty_points'))['total'] or 0
    
    context = {
        'vehicle': vehicle,
        'challans': challans,
        'total_fines': total_fines,
        'total_points': total_points,
    }
    
    return render(request, 'challan_app/vehicle_detail.html', context)

@login_required
def vehicle_create(request):
    """Create a new vehicle"""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Vehicle {vehicle.registration_number} created successfully.')
            return redirect('challan_app:vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = VehicleForm()
    
    context = {
        'form': form,
        'title': 'Add New Vehicle',
    }
    
    return render(request, 'challan_app/vehicle_form.html', context)

@login_required
def vehicle_edit(request, vehicle_id):
    """Edit an existing vehicle"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehicle {vehicle.registration_number} updated successfully.')
            return redirect('challan_app:vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = VehicleForm(instance=vehicle)
    
    context = {
        'form': form,
        'vehicle': vehicle,
        'title': f'Edit Vehicle {vehicle.registration_number}',
    }
    
    return render(request, 'challan_app/vehicle_form.html', context)

@login_required
def challan_list(request):
    """List all challans"""
    challans = Challan.objects.select_related('vehicle', 'violation_type', 'issued_by').order_by('-issued_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        challans = challans.filter(status=status_filter)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        challans = challans.filter(
            Q(challan_number__icontains=query) |
            Q(vehicle__registration_number__icontains=query) |
            Q(vehicle__owner_name__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(challans, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'status_choices': Challan.STATUS_CHOICES,
    }
    
    return render(request, 'challan_app/challan_list.html', context)

@login_required
def challan_detail(request, challan_id):
    """Show challan details"""
    challan = get_object_or_404(Challan, id=challan_id)
    evidence = ViolationEvidence.objects.filter(challan=challan)
    
    try:
        payment = Payment.objects.get(challan=challan)
    except Payment.DoesNotExist:
        payment = None
    
    context = {
        'challan': challan,
        'evidence': evidence,
        'payment': payment,
    }
    
    return render(request, 'challan_app/challan_detail.html', context)

@login_required
def challan_create(request):
    """Create a new challan"""
    if request.method == 'POST':
        form = ChallanForm(request.POST)
        if form.is_valid():
            challan = form.save(commit=False)
            challan.issued_by = request.user
            challan.save()
            messages.success(request, f'Challan {challan.challan_number} created successfully.')
            return redirect('challan_app:challan_detail', challan_id=challan.id)
    else:
        form = ChallanForm()
    
    context = {
        'form': form,
        'title': 'Issue New Challan',
    }
    
    return render(request, 'challan_app/challan_form.html', context)

@login_required
def challan_edit(request, challan_id):
    """Edit an existing challan"""
    challan = get_object_or_404(Challan, id=challan_id)
    
    if request.method == 'POST':
        form = ChallanForm(request.POST, instance=challan)
        if form.is_valid():
            form.save()
            messages.success(request, f'Challan {challan.challan_number} updated successfully.')
            return redirect('challan_app:challan_detail', challan_id=challan.id)
    else:
        form = ChallanForm(instance=challan)
    
    context = {
        'form': form,
        'challan': challan,
        'title': f'Edit Challan {challan.challan_number}',
    }
    
    return render(request, 'challan_app/challan_form.html', context)

@login_required
def challan_status_update(request, challan_id):
    """Update challan status via AJAX"""
    if request.method == 'POST':
        challan = get_object_or_404(Challan, id=challan_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Challan.STATUS_CHOICES):
            challan.status = new_status
            if new_status == 'PAID':
                challan.paid_at = timezone.now()
            challan.save()
            
            return JsonResponse({
                'success': True,
                'status': new_status,
                'message': f'Challan status updated to {new_status}'
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Invalid status'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def reports(request):
    """Generate reports and analytics"""
    # Date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Challan statistics by date
    daily_challans = Challan.objects.filter(
        issued_at__range=[start_date, end_date]
    ).extra(
        select={'day': 'date(issued_at)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Violation type statistics
    violation_stats = Challan.objects.filter(
        issued_at__range=[start_date, end_date]
    ).values('violation_type__name').annotate(
        count=Count('id'),
        total_fine=Sum('fine_amount')
    ).order_by('-count')
    
    # Revenue statistics
    total_revenue = Challan.objects.filter(
        status='PAID',
        issued_at__range=[start_date, end_date]
    ).aggregate(total=Sum('fine_amount'))['total'] or 0
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'daily_challans': daily_challans,
        'violation_stats': violation_stats,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'challan_app/reports.html', context)

@login_required
def api_vehicle_search(request):
    """API endpoint for vehicle search"""
    query = request.GET.get('q', '')
    if len(query) < 3:
        return JsonResponse({'vehicles': []})
    
    vehicles = Vehicle.objects.filter(
        Q(registration_number__icontains=query) |
        Q(owner_name__icontains=query)
    )[:10]
    
    vehicle_data = [{
        'id': str(vehicle.id),
        'registration_number': vehicle.registration_number,
        'owner_name': vehicle.owner_name,
        'vehicle_type': vehicle.get_vehicle_type_display(),
    } for vehicle in vehicles]
    
    return JsonResponse({'vehicles': vehicle_data})
