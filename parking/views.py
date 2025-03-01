from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from .models import Vehicle, ParkingRecord, ParkingSlot, ParkingOperator, Shift, ShiftLog, ParkingRate, Language, BackupHistory
from .anpr import ANPR
from PIL import Image
import json
from datetime import timedelta, datetime
from django.db.models import Sum, Q, F, Count, Avg
from collections import defaultdict
from django.contrib.auth import logout

anpr_system = ANPR()

@login_required
def dashboard(request):
    # Dummy statistics data
    total_vehicles = 150
    active_parkings = 45
    available_slots = 55
    today_income = 2750000

    # Dummy recent activities
    recent_activities = [
        {
            'timestamp': timezone.now() - timezone.timedelta(minutes=5),
            'license_plate': 'B 1234 ABC',
            'vehicle_type': 'Mobil',
            'status': 'entry',
            'fee': None
        },
        {
            'timestamp': timezone.now() - timezone.timedelta(minutes=15),
            'license_plate': 'B 5678 DEF',
            'vehicle_type': 'Motor',
            'status': 'exit',
            'fee': 15000
        },
        {
            'timestamp': timezone.now() - timezone.timedelta(minutes=25),
            'license_plate': 'B 9012 GHI',
            'vehicle_type': 'Mobil',
            'status': 'exit',
            'fee': 25000
        },
        {
            'timestamp': timezone.now() - timezone.timedelta(minutes=35),
            'license_plate': 'B 3456 JKL',
            'vehicle_type': 'Motor',
            'status': 'entry',
            'fee': None
        },
        {
            'timestamp': timezone.now() - timezone.timedelta(minutes=45),
            'license_plate': 'B 7890 MNO',
            'vehicle_type': 'Mobil',
            'status': 'exit',
            'fee': 30000
        }
    ]

    # Define menu items
    menus = [
        {
            'title': 'Kendaraan Masuk',
            'description': 'Catat kendaraan yang masuk ke area parkir',
            'icon': 'fa-car-side',
            'color': 'text-primary',
            'url': 'parking:vehicle_entry',
            'button_color': 'btn-primary',
            'button_text': 'Masuk'
        },
        {
            'title': 'Kendaraan Keluar',
            'description': 'Proses kendaraan yang akan keluar dari area parkir',
            'icon': 'fa-car',
            'color': 'text-success',
            'url': 'parking:vehicle_exit',
            'button_color': 'btn-success',
            'button_text': 'Keluar'
        },
        {
            'title': 'Riwayat Parkir',
            'description': 'Lihat riwayat parkir kendaraan',
            'icon': 'fa-history',
            'color': 'text-info',
            'url': 'parking:history',
            'button_color': 'btn-info text-white',
            'button_text': 'Riwayat'
        },
        {
            'title': 'Pengaturan',
            'description': 'Atur konfigurasi sistem parkir',
            'icon': 'fa-cog',
            'color': 'text-secondary',
            'url': 'parking:settings',
            'button_color': 'btn-secondary',
            'button_text': 'Pengaturan'
        },
        {
            'title': 'Laporan',
            'description': 'Lihat laporan dan statistik parkir',
            'icon': 'fa-chart-bar',
            'color': 'text-warning',
            'url': 'parking:reports',
            'button_color': 'btn-warning',
            'button_text': 'Laporan'
        },
        {
            'title': 'Analitik',
            'description': 'Lihat analisis data parkir',
            'icon': 'fa-chart-line',
            'color': 'text-danger',
            'url': 'parking:analytics',
            'button_color': 'btn-danger',
            'button_text': 'Analitik'
        }
    ]

    context = {
        'total_vehicles': total_vehicles,
        'occupied_slots': active_parkings,
        'available_slots': available_slots,
        'today_income': today_income,
        'menus': menus,
        'recent_activities': recent_activities,
        'current_time': timezone.now()
    }
    
    return render(request, 'parking/dashboard.html', context)

@login_required
def vehicle_entry(request):
    if request.method == 'POST':
        try:
            # Get image from request
            image_file = request.FILES.get('vehicle_image')
            if not image_file:
                return JsonResponse({'error': 'No image provided'}, status=400)
            
            # Process image with ANPR
            image = Image.open(image_file)
            plate_number = anpr_system.detect_plate(image)
            
            if not plate_number:
                return JsonResponse({'error': 'Could not detect plate number'}, status=400)
            
            # Check if this is just for plate detection
            if request.POST.get('detect_only') == 'true':
                return JsonResponse({
                    'success': True,
                    'plate_number': plate_number
                })
            
            # Create or get vehicle
            vehicle_type = request.POST.get('vehicle_type', 'CAR')
            vehicle = Vehicle.objects.create(
                plate_number=plate_number,
                vehicle_type=vehicle_type,
                entry_image=image_file
            )
            
            # Create parking record
            parking_record = ParkingRecord.objects.create(
                vehicle=vehicle,
                operator=request.user
            )
            
            # Find and assign parking slot
            available_slot = ParkingSlot.objects.filter(
                slot_type=vehicle_type,
                is_occupied=False
            ).first()
            
            if available_slot:
                available_slot.is_occupied = True
                available_slot.current_vehicle = vehicle
                available_slot.save()
            
            return JsonResponse({
                'success': True,
                'plate_number': plate_number,
                'parking_id': parking_record.id,
                'slot_number': available_slot.slot_number if available_slot else None
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'parking/vehicle_entry.html')

@login_required
def vehicle_exit(request):
    if request.method == 'POST':
        try:
            # Get parking record
            parking_id = request.POST.get('parking_id')
            parking_record = get_object_or_404(ParkingRecord, id=parking_id, exit_time__isnull=True)
            
            # Get exit image
            exit_image = request.FILES.get('exit_image')
            if not exit_image:
                return JsonResponse({'error': 'No exit image provided'}, status=400)
            
            # Update vehicle with exit image
            parking_record.vehicle.exit_image = exit_image
            parking_record.vehicle.save()
            
            # Compare entry and exit images
            image_match_score = anpr_system.compare_images(
                parking_record.vehicle.entry_image.path,
                parking_record.vehicle.exit_image.path
            )
            
            # Update parking record
            parking_record.exit_time = timezone.now()
            parking_record.image_match_score = image_match_score
            parking_record.fee = parking_record.calculate_fee()
            parking_record.save()
            
            # Free up parking slot
            slot = parking_record.vehicle.parking_slot
            if slot:
                slot.is_occupied = False
                slot.current_vehicle = None
                slot.save()
            
            return JsonResponse({
                'success': True,
                'fee': parking_record.fee,
                'image_match_score': image_match_score,
                'duration': (parking_record.exit_time - parking_record.entry_time).total_seconds() / 3600
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'parking/vehicle_exit.html')

@login_required
def parking_history(request):
    records = ParkingRecord.objects.all().order_by('-entry_time')
    return render(request, 'parking/history.html', {'records': records})

@login_required
def manage_slots(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        slot_id = request.POST.get('slot_id')
        
        if action == 'add':
            slot_type = request.POST.get('slot_type')
            slot_number = request.POST.get('slot_number')
            
            ParkingSlot.objects.create(
                slot_number=slot_number,
                slot_type=slot_type
            )
            messages.success(request, 'Parking slot added successfully')
            
        elif action == 'delete':
            slot = get_object_or_404(ParkingSlot, id=slot_id)
            if not slot.is_occupied:
                slot.delete()
                messages.success(request, 'Parking slot deleted successfully')
            else:
                messages.error(request, 'Cannot delete occupied parking slot')
    
    slots = ParkingSlot.objects.all().order_by('slot_type', 'slot_number')
    return render(request, 'parking/manage_slots.html', {'slots': slots})

@login_required
def reports(request):
    # Get date range from request or use defaults
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    filter_type = request.GET.get('filter', 'today')

    # Parse custom date range if provided
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
            end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
            filter_type = 'custom'
        except ValueError:
            start_date = None
            end_date = None

    # Get date range based on filter
    if not (start_date and end_date):
        if filter_type == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
            filter_display = 'Minggu Ini'
        elif filter_type == 'month':
            start_date = today.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            filter_display = 'Bulan Ini'
        elif filter_type == 'year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            filter_display = 'Tahun Ini'
        else:  # today
            start_date = today
            end_date = today
            filter_display = 'Hari Ini'

    # Get statistics for today and yesterday
    today_records = ParkingRecord.objects.filter(entry_time__date=today)
    yesterday_records = ParkingRecord.objects.filter(entry_time__date=yesterday)
    
    # Calculate growth rates
    today_vehicles = today_records.count()
    yesterday_vehicles = yesterday_records.count()
    vehicle_growth = ((today_vehicles - yesterday_vehicles) / (yesterday_vehicles or 1)) * 100

    today_income = today_records.filter(is_paid=True).aggregate(total=Sum('fee'))['total'] or 0
    yesterday_income = yesterday_records.filter(is_paid=True).aggregate(total=Sum('fee'))['total'] or 0
    income_growth = ((today_income - yesterday_income) / (yesterday_income or 1)) * 100

    # Calculate average durations
    def calc_avg_duration(records):
        completed = records.filter(exit_time__isnull=False)
        if completed.exists():
            total_duration = sum((r.exit_time - r.entry_time) for r in completed)
            return total_duration / completed.count()
        return timedelta(0)

    avg_duration = calc_avg_duration(today_records)
    yesterday_avg_duration = calc_avg_duration(yesterday_records)
    duration_growth = ((avg_duration.total_seconds() - yesterday_avg_duration.total_seconds()) / 
                      (yesterday_avg_duration.total_seconds() or 1)) * 100

    # Calculate occupancy rates
    total_slots = ParkingSlot.objects.count()
    current_occupied = ParkingSlot.objects.filter(is_occupied=True).count()
    yesterday_occupied = ParkingRecord.objects.filter(
        entry_time__date=yesterday,
        exit_time__isnull=True
    ).count()
    
    occupancy_rate = (current_occupied / total_slots) * 100 if total_slots > 0 else 0
    yesterday_occupancy = (yesterday_occupied / total_slots) * 100 if total_slots > 0 else 0
    occupancy_growth = occupancy_rate - yesterday_occupancy

    # Get daily reports for the date range
    reports = []
    revenue_data = []
    revenue_dates = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_records = ParkingRecord.objects.filter(entry_time__date=current_date)
        
        # Get vehicle counts by type
        cars = daily_records.filter(vehicle__vehicle_type='CAR').count()
        motorcycles = daily_records.filter(vehicle__vehicle_type='MOTORCYCLE').count()
        trucks = daily_records.filter(vehicle__vehicle_type='TRUCK').count()
        
        # Calculate daily income
        daily_income = daily_records.filter(is_paid=True).aggregate(
            total=Sum('fee'))['total'] or 0
        
        # Calculate average duration and occupancy for the day
        avg_dur = calc_avg_duration(daily_records)
        max_occupied = daily_records.filter(exit_time__isnull=True).count()
        daily_occupancy = (max_occupied / total_slots) * 100 if total_slots > 0 else 0
        
        reports.append({
            'date': current_date,
            'total_vehicles': daily_records.count(),
            'cars': cars,
            'motorcycles': motorcycles,
            'trucks': trucks,
            'income': daily_income,
            'avg_duration': avg_dur,
            'occupancy_rate': round(daily_occupancy, 1)
        })
        
        revenue_data.append(daily_income)
        revenue_dates.append(current_date.strftime('%d/%m/%Y'))
        
        current_date += timedelta(days=1)

    # Calculate vehicle distribution for pie chart
    total_cars = ParkingRecord.objects.filter(
        entry_time__date__range=[start_date, end_date],
        vehicle__vehicle_type='CAR'
    ).count()
    total_motorcycles = ParkingRecord.objects.filter(
        entry_time__date__range=[start_date, end_date],
        vehicle__vehicle_type='MOTORCYCLE'
    ).count()
    total_trucks = ParkingRecord.objects.filter(
        entry_time__date__range=[start_date, end_date],
        vehicle__vehicle_type='TRUCK'
    ).count()
    
    vehicle_distribution = [total_cars, total_motorcycles, total_trucks]

    # Calculate hourly statistics
    hourly_entries = [0] * 24
    hourly_exits = [0] * 24
    
    today_entries = ParkingRecord.objects.filter(entry_time__date=today)
    today_exits = ParkingRecord.objects.filter(exit_time__date=today)
    
    for record in today_entries:
        hour = record.entry_time.hour
        hourly_entries[hour] += 1
    
    for record in today_exits:
        hour = record.exit_time.hour
        hourly_exits[hour] += 1

    context = {
        'today_vehicles': today_vehicles,
        'today_income': today_income,
        'avg_duration': avg_duration,
        'occupancy_rate': round(occupancy_rate, 1),
        'vehicle_growth': round(vehicle_growth, 1),
        'income_growth': round(income_growth, 1),
        'duration_growth': round(duration_growth, 1),
        'occupancy_growth': round(occupancy_growth, 1),
        'reports': reports,
        'filter': filter_type,
        'filter_display': filter_display,
        'revenue_data': revenue_data,
        'revenue_dates': revenue_dates,
        'vehicle_distribution': vehicle_distribution,
        'hourly_entries': hourly_entries,
        'hourly_exits': hourly_exits,
    }
    
    return render(request, 'parking/reports.html', context)

@login_required
def analytics(request):
    # Dummy data for analytics
    current_month = timezone.now().month
    current_year = timezone.now().year

    # Monthly revenue data
    monthly_revenue = [
        2500000,  # January
        2750000,  # February
        3000000,  # March
        3250000,  # April
        3500000,  # May
        3750000,  # June
        4000000,  # July
        4250000,  # August
        4500000,  # September
        4750000,  # October
        5000000,  # November
        5250000,  # December
    ]

    # Vehicle type distribution
    vehicle_distribution = {
        'Mobil': 60,
        'Motor': 35,
        'Truk': 5
    }

    # Hourly occupancy rate
    hourly_occupancy = [
        20,  # 00:00
        15,  # 01:00
        10,  # 02:00
        5,   # 03:00
        5,   # 04:00
        10,  # 05:00
        30,  # 06:00
        60,  # 07:00
        85,  # 08:00
        95,  # 09:00
        90,  # 10:00
        85,  # 11:00
        80,  # 12:00
        75,  # 13:00
        70,  # 14:00
        65,  # 15:00
        70,  # 16:00
        80,  # 17:00
        85,  # 18:00
        75,  # 19:00
        60,  # 20:00
        45,  # 21:00
        35,  # 22:00
        25,  # 23:00
    ]

    # Recent transactions
    recent_transactions = [
        {
            'date': timezone.now() - timezone.timedelta(hours=1),
            'plate': 'B 1234 ABC',
            'duration': '2.5 jam',
            'amount': 25000,
            'amount_formatted': f"Rp {25000:,.0f}"
        },
        {
            'date': timezone.now() - timezone.timedelta(hours=2),
            'plate': 'B 5678 DEF',
            'duration': '1.5 jam',
            'amount': 15000,
            'amount_formatted': f"Rp {15000:,.0f}"
        },
        {
            'date': timezone.now() - timezone.timedelta(hours=3),
            'plate': 'B 9012 GHI',
            'duration': '3 jam',
            'amount': 30000,
            'amount_formatted': f"Rp {30000:,.0f}"
        },
        {
            'date': timezone.now() - timezone.timedelta(hours=4),
            'plate': 'B 3456 JKL',
            'duration': '4 jam',
            'amount': 40000,
            'amount_formatted': f"Rp {40000:,.0f}"
        },
        {
            'date': timezone.now() - timezone.timedelta(hours=5),
            'plate': 'B 7890 MNO',
            'duration': '2 jam',
            'amount': 20000,
            'amount_formatted': f"Rp {20000:,.0f}"
        }
    ]

    # Performance metrics
    total_revenue = sum(monthly_revenue)
    performance_metrics = {
        'total_revenue': total_revenue,
        'total_revenue_formatted': f"Rp {total_revenue:,.0f}",
        'avg_daily_revenue': total_revenue / 30,
        'avg_daily_revenue_formatted': f"Rp {(total_revenue / 30):,.0f}",
        'total_vehicles': 1500,
        'avg_duration': '2.5 jam',
        'occupancy_rate': 75,
        'peak_hour': '09:00',
        'most_common_type': 'Mobil'
    }

    context = {
        'monthly_revenue': monthly_revenue,
        'current_month': current_month,
        'current_year': current_year,
        'vehicle_distribution': vehicle_distribution,
        'hourly_occupancy': hourly_occupancy,
        'recent_transactions': recent_transactions,
        'performance_metrics': performance_metrics,
    }

    return render(request, 'parking/analytics.html', context)

@login_required
def manage_operators(request):
    operators = ParkingOperator.objects.all().order_by('-created_at')
    return render(request, 'parking/manage_operators.html', {'operators': operators})

@login_required
def manage_shifts(request):
    # Get filter parameters
    date = request.GET.get('date')
    operator_id = request.GET.get('operator')
    
    # Base queryset
    shifts = Shift.objects.all().order_by('-date', 'start_time')
    
    # Apply filters
    if date:
        shifts = shifts.filter(date=date)
    if operator_id:
        shifts = shifts.filter(operator_id=operator_id)
    
    operators = ParkingOperator.objects.filter(is_active=True)
    
    return render(request, 'parking/manage_shifts.html', {
        'shifts': shifts,
        'operators': operators
    })

@login_required
def manage_rates(request):
    rates = ParkingRate.objects.all().order_by('vehicle_type')
    return render(request, 'parking/manage_rates.html', {'rates': rates})

@login_required
def settings(request):
    """View for system settings."""
    languages = Language.objects.all()
    backup_history = BackupHistory.objects.all().order_by('-created_at')[:10]
    last_backup = BackupHistory.objects.filter(
        type__in=['MANUAL', 'AUTO'], 
        status='Success'
    ).order_by('-created_at').first()

    context = {
        'languages': languages,
        'backup_history': backup_history,
        'last_backup': last_backup.created_at if last_backup else None,
    }
    return render(request, 'parking/settings.html', context)

@login_required
def change_language(request):
    """API endpoint to change system language."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lang_code = data.get('language')
            
            if not lang_code:
                return JsonResponse({'error': 'Kode bahasa tidak valid'}, status=400)
            
            language = Language.objects.filter(code=lang_code).first()
            if not language:
                return JsonResponse({'error': 'Bahasa tidak ditemukan'}, status=404)
            
            # Set as default and save
            language.is_default = True
            language.save()
            
            return JsonResponse({'message': 'Bahasa berhasil diubah'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON tidak valid'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Metode tidak diizinkan'}, status=405)

# API Views for AJAX operations
@login_required
def operator_api(request, operator_id=None):
    if request.method == 'GET':
        if operator_id:
            operator = get_object_or_404(ParkingOperator, id=operator_id)
            data = {
                'id': operator.id,
                'employee_id': operator.employee_id,
                'user': {
                    'first_name': operator.user.first_name,
                    'last_name': operator.user.last_name,
                    'email': operator.user.email,
                },
                'phone_number': operator.phone_number,
                'address': operator.address,
                'is_active': operator.is_active
            }
            return JsonResponse(data)
        
    elif request.method == 'POST':
        # Create new operator
        user = User.objects.create_user(
            username=request.POST['email'],
            email=request.POST['email'],
            password=request.POST['password'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name']
        )
        
        operator = ParkingOperator.objects.create(
            user=user,
            employee_id=request.POST['employee_id'],
            phone_number=request.POST['phone_number'],
            address=request.POST['address']
        )
        return JsonResponse({'status': 'success'})
        
    elif request.method == 'DELETE' and operator_id:
        operator = get_object_or_404(ParkingOperator, id=operator_id)
        operator.is_active = False
        operator.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def shift_api(request, shift_id=None):
    if request.method == 'GET':
        if shift_id:
            shift = get_object_or_404(Shift, id=shift_id)
            data = {
                'id': shift.id,
                'operator': shift.operator_id,
                'shift_type': shift.shift_type,
                'date': shift.date.isoformat(),
                'start_time': shift.start_time.strftime('%H:%M'),
                'end_time': shift.end_time.strftime('%H:%M'),
                'is_active': shift.is_active
            }
            return JsonResponse(data)
            
    elif request.method == 'POST':
        # Create new shift
        shift_type = request.POST['shift_type']
        shift_times = {
            'pagi': ('06:00', '14:00'),
            'siang': ('14:00', '22:00'),
            'malam': ('22:00', '06:00')
        }
        start_time, end_time = shift_times[shift_type]
        
        shift = Shift.objects.create(
            operator_id=request.POST['operator'],
            shift_type=shift_type,
            date=request.POST['date'],
            start_time=start_time,
            end_time=end_time
        )
        return JsonResponse({'status': 'success'})
        
    elif request.method == 'DELETE' and shift_id:
        shift = get_object_or_404(Shift, id=shift_id)
        shift.is_active = False
        shift.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def shift_log_api(request, shift_id):
    shift_log = get_object_or_404(ShiftLog, shift_id=shift_id)
    data = {
        'check_in': shift_log.check_in.strftime('%Y-%m-%d %H:%M:%S'),
        'check_out': shift_log.check_out.strftime('%Y-%m-%d %H:%M:%S'),
        'total_transactions': shift_log.total_transactions,
        'total_revenue': float(shift_log.total_revenue),
        'notes': shift_log.notes
    }
    return JsonResponse(data)

@login_required
def rate_api(request):
    if request.method == 'POST':
        rates_data = request.POST.getlist('rates[]')
        for rate_data in rates_data:
            rate = ParkingRate.objects.get(id=rate_data['id'])
            rate.base_rate = rate_data['base_rate']
            rate.grace_period_minutes = rate_data['grace_period_minutes']
            rate.daily_max_rate = rate_data['daily_max_rate']
            rate.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def settings_api(request, action):
    if request.method == 'POST':
        if action == 'language':
            data = json.loads(request.body)
            lang_code = data.get('language')
            if lang_code:
                # Update default language
                Language.objects.filter(is_default=True).update(is_default=False)
                Language.objects.filter(code=lang_code).update(is_default=True)
                return JsonResponse({'status': 'success'})
        
        elif action == 'backup':
            from django.core import management
            import os
            from django.conf import settings
            
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup name with timestamp
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}')
            
            try:
                # Call the backup management command
                management.call_command('backup_restore', action='backup', backup_path=backup_path)
                
                # Create a zip file of the backup
                import shutil
                shutil.make_archive(backup_path, 'zip', backup_path)
                zip_file = f"{backup_path}.zip"
                
                # Record backup in history
                file_size = os.path.getsize(zip_file)
                BackupHistory.objects.create(
                    type='MANUAL',
                    created_by=request.user,
                    file_size=file_size,
                    status='Success'
                )
                
                # Prepare the response
                with open(zip_file, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="parking_backup_{timestamp}.zip"'
                
                # Clean up the temporary files
                shutil.rmtree(backup_path)
                os.remove(zip_file)
                
                return response
            except Exception as e:
                # Record failed backup attempt
                BackupHistory.objects.create(
                    type='MANUAL',
                    created_by=request.user,
                    file_size=0,
                    status='Failed',
                    notes=str(e)
                )
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
        elif action == 'restore':
            import tempfile
            import zipfile
            
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No file provided'}, status=400)
            
            try:
                backup_file = request.FILES['file']
                
                # Create a temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save the uploaded zip file
                    temp_zip = os.path.join(temp_dir, 'backup.zip')
                    with open(temp_zip, 'wb') as f:
                        for chunk in backup_file.chunks():
                            f.write(chunk)
                    
                    # Extract the zip file
                    backup_path = os.path.join(temp_dir, 'backup')
                    os.makedirs(backup_path)
                    with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                        zip_ref.extractall(backup_path)
                    
                    # Call the restore management command
                    management.call_command('backup_restore', action='restore', backup_path=backup_path)
                    
                    # Record successful restore
                    BackupHistory.objects.create(
                        type='RESTORE',
                        created_by=request.user,
                        file_size=backup_file.size,
                        status='Success'
                    )
                
                return JsonResponse({'status': 'success'})
            except Exception as e:
                # Record failed restore attempt
                BackupHistory.objects.create(
                    type='RESTORE',
                    created_by=request.user,
                    file_size=backup_file.size if 'backup_file' in locals() else 0,
                    status='Failed',
                    notes=str(e)
                )
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def logout_view(request):
    logout(request)
    return redirect('login')
