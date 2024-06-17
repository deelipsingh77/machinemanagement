from django.contrib import admin

from core.models import Machine, MaintenanceTask, Part

# Register your models here.
@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name',)

@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'machine', 'task_name', 'scheduled_date', 'completed')
    list_filter = ('machine', 'scheduled_date', 'completed')
    search_fields = ('machine__name', 'task_name')

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'quantity')
    search_fields = ('name', 'description')
    list_filter = ('name',)