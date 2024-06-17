from django.contrib import admin
from .models import Machine, Part, Maintenance

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'price')
    search_fields = ('name', 'serial_number')

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'part_number', 'price')
    search_fields = ('name', 'part_number')

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('machine', 'date', 'get_parts_used', 'description')
    list_filter = ('machine', 'date')
    search_fields = ('machine__name', 'description')

    def get_parts_used(self, obj):
        return ", ".join([part.name for part in obj.parts_used.all()])
    get_parts_used.short_description = 'Parts Used'
