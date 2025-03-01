from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('CAR', 'Car'),
        ('MOTORCYCLE', 'Motorcycle'),
        ('TRUCK', 'Truck'),
    ]
    
    plate_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    entry_image = models.ImageField(upload_to='vehicle_images/entry/')
    exit_image = models.ImageField(upload_to='vehicle_images/exit/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.plate_number

class ParkingRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image_match_score = models.FloatField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.entry_time}"

    def calculate_fee(self):
        if not self.exit_time:
            return None
        
        duration = self.exit_time - self.entry_time
        hours = duration.total_seconds() / 3600
        
        # Base rates per vehicle type
        rates = {
            'CAR': 5000,  # Rp. 5,000 per hour
            'MOTORCYCLE': 2000,  # Rp. 2,000 per hour
            'TRUCK': 10000,  # Rp. 10,000 per hour
        }
        
        base_rate = rates.get(self.vehicle.vehicle_type, 5000)
        total_fee = base_rate * hours
        
        # Round up to the nearest hour
        return round(total_fee)

class ParkingSlot(models.Model):
    SLOT_TYPES = [
        ('CAR', 'Car'),
        ('MOTORCYCLE', 'Motorcycle'),
        ('TRUCK', 'Truck'),
    ]
    
    slot_number = models.CharField(max_length=10)
    slot_type = models.CharField(max_length=10, choices=SLOT_TYPES)
    is_occupied = models.BooleanField(default=False)
    current_vehicle = models.OneToOneField(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='parking_slot'
    )

    def __str__(self):
        return f"{self.slot_type} - {self.slot_number}"

class ParkingOperator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class Shift(models.Model):
    SHIFT_CHOICES = [
        ('pagi', 'Pagi (06:00-14:00)'),
        ('siang', 'Siang (14:00-22:00)'),
        ('malam', 'Malam (22:00-06:00)'),
    ]

    operator = models.ForeignKey(ParkingOperator, on_delete=models.CASCADE)
    shift_type = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('operator', 'date', 'shift_type')

    def __str__(self):
        return f"{self.operator.user.get_full_name()} - {self.get_shift_type_display()} ({self.date})"

class ShiftLog(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    total_transactions = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Log: {self.shift} ({self.check_in} - {self.check_out})"

class ParkingRate(models.Model):
    VEHICLE_TYPES = [
        ('CAR', 'Car'),
        ('MOTORCYCLE', 'Motorcycle'),
        ('TRUCK', 'Truck'),
    ]
    
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, unique=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base rate per hour")
    grace_period_minutes = models.IntegerField(default=15, help_text="Grace period in minutes")
    daily_max_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum rate for 24 hours")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_vehicle_type_display()} - Rp {self.base_rate}/hour"

class Language(models.Model):
    LANGUAGE_CHOICES = [
        ('id', 'Bahasa Indonesia'),
        ('en', 'English'),
        ('jw', 'Basa Jawa'),
        ('su', 'Basa Sunda'),
    ]
    
    code = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, unique=True)
    name = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # If this is the first language being added, make it default
        if not Language.objects.exists():
            self.is_default = True
        elif self.is_default:
            # If setting this language as default, unset others
            Language.objects.all().update(is_default=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = 'Bahasa'
        verbose_name_plural = 'Bahasa'

class BackupHistory(models.Model):
    BACKUP_TYPES = [
        ('MANUAL', 'Manual Backup'),
        ('AUTO', 'Automatic Backup'),
        ('RESTORE', 'Database Restore'),
    ]
    
    type = models.CharField(max_length=10, choices=BACKUP_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    file_size = models.BigIntegerField(help_text="Size in bytes")
    status = models.CharField(max_length=50, default="Success")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Backup histories"

    def __str__(self):
        return f"{self.get_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
