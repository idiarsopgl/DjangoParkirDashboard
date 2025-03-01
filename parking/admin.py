from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Vehicle, ParkingRecord, ParkingSlot, ParkingOperator, Shift, ShiftLog, ParkingRate, Language, BackupHistory

# Register your models here.

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'vehicle_type', 'created_at', 'updated_at')
    search_fields = ('plate_number',)
    list_filter = ('vehicle_type',)

class ParkingRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'entry_time', 'exit_time', 'fee', 'is_paid')
    search_fields = ('vehicle__plate_number',)
    list_filter = ('entry_time', 'exit_time', 'is_paid')

class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = ('slot_number', 'slot_type', 'is_occupied', 'current_vehicle')
    list_filter = ('slot_type', 'is_occupied')
    search_fields = ('slot_number',)

class ParkingOperatorAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'phone_number', 'is_active')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'phone_number')
    list_filter = ('is_active',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

class ShiftAdmin(admin.ModelAdmin):
    list_display = ('date', 'shift_type', 'operator', 'start_time', 'end_time', 'is_active')
    list_filter = ('shift_type', 'date', 'is_active')
    search_fields = ('operator__employee_id', 'operator__user__first_name', 'operator__user__last_name')

class ShiftLogAdmin(admin.ModelAdmin):
    list_display = ('shift', 'check_in', 'check_out', 'total_transactions', 'total_revenue')
    list_filter = ('shift__date', 'shift__shift_type')
    search_fields = ('shift__operator__employee_id',)

@admin.register(ParkingRate)
class ParkingRateAdmin(admin.ModelAdmin):
    list_display = ('get_vehicle_type_display', 'base_rate', 'grace_period_minutes', 'daily_max_rate', 'updated_at')
    list_filter = ('vehicle_type',)
    search_fields = ('vehicle_type',)
    ordering = ('vehicle_type',)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_default', 'updated_at')
    list_filter = ('is_default',)
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(BackupHistory)
class BackupHistoryAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'type', 'created_by', 'status', 'file_size')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('created_by__username', 'notes')
    readonly_fields = ('created_at', 'created_by', 'file_size')
    ordering = ('-created_at',)

admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(ParkingRecord, ParkingRecordAdmin)
admin.site.register(ParkingSlot, ParkingSlotAdmin)
admin.site.register(ParkingOperator, ParkingOperatorAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(ShiftLog, ShiftLogAdmin)
