from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('entry/', views.vehicle_entry, name='vehicle_entry'),
    path('exit/', views.vehicle_exit, name='vehicle_exit'),
    path('history/', views.parking_history, name='history'),
    path('manage-slots/', views.manage_slots, name='manage_slots'),
    path('reports/', views.reports, name='reports'),
    path('analytics/', views.analytics, name='analytics'),
    path('manage_slots/', views.manage_slots, name='manage_slots'),
    path('manage_operators/', views.manage_operators, name='manage_operators'),
    path('manage_shifts/', views.manage_shifts, name='manage_shifts'),
    path('manage_rates/', views.manage_rates, name='manage_rates'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api/operators/', views.operator_api, name='operator_api'),
    path('api/operators/<int:operator_id>/', views.operator_api, name='operator_detail_api'),
    path('api/shifts/', views.shift_api, name='shift_api'),
    path('api/shifts/<int:shift_id>/', views.shift_api, name='shift_detail_api'),
    path('api/shifts/<int:shift_id>/log/', views.shift_log_api, name='shift_log_api'),
    path('api/rates/', views.rate_api, name='rate_api'),
    path('api/settings/<str:action>/', views.settings_api, name='settings_api'),
]
