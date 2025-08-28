from django.urls import path
from . import views

app_name = 'challan_app'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Vehicles
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/create/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<uuid:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<uuid:vehicle_id>/edit/', views.vehicle_edit, name='vehicle_edit'),
    
    # Challans
    path('challans/', views.challan_list, name='challan_list'),
    path('challans/create/', views.challan_create, name='challan_create'),
    path('challans/<uuid:challan_id>/', views.challan_detail, name='challan_detail'),
    path('challans/<uuid:challan_id>/edit/', views.challan_edit, name='challan_edit'),
    path('challans/<uuid:challan_id>/status/', views.challan_status_update, name='challan_status_update'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
    
    # API endpoints
    path('api/vehicle-search/', views.api_vehicle_search, name='api_vehicle_search'),
]
