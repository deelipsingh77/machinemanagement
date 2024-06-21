from django.contrib import admin
from .models import Location, Machine, Part, MachinePart, Ticket, TicketResolution

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location',)
    search_fields = ('location',)
    
@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('machine_no', 'machine_name', 'purchase_date', 'machine_warranty', 'location', 'price')
    list_filter = ('location', 'purchase_date')
    search_fields = ('machine_no', 'machine_name')

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('part_no', 'part_name', 'purchase_date', 'part_warranty' ,'quantity', 'location', 'price')
    list_filter = ('location', 'purchase_date')
    search_fields = ('part_no', 'part_name')

@admin.register(MachinePart)
class MachinePartAdmin(admin.ModelAdmin):
    list_display = ('machine', 'part', 'location')
    list_filter = ('machine', 'part')
    search_fields = ('machine__machine_name', 'part__part_name')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('select_ticket', 'machine', 'ticket_status', 'assigned_user')
    list_filter = ('ticket_status', 'machine__machine_name')
    search_fields = ('select_ticket', 'machine__machine_name')

@admin.register(TicketResolution)
class TicketResolutionAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'resolved_by', 'resolution_status', 'resolution_date')
    list_filter = ('resolution_status', 'resolved_by')
    search_fields = ('ticket__select_ticket', 'resolved_by__username')

