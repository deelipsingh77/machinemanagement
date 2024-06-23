from django.contrib import admin
from .models import Issue, Location, Machine, Part, MachinePart, Ticket, TicketResolution

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location',)
    search_fields = ('location',)
    
@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('id', 'machine_name', 'purchase_date', 'machine_warranty', 'location', 'price')
    list_filter = ('location', 'purchase_date')
    search_fields = ('id', 'machine_name')

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('id', 'part_name', 'purchase_date', 'part_warranty' ,'quantity', 'location', 'price')
    list_filter = ('location', 'purchase_date')
    search_fields = ('id', 'part_name')

@admin.register(MachinePart)
class MachinePartAdmin(admin.ModelAdmin):
    list_display = ('machine', 'part', 'location')
    list_filter = ('machine', 'part')
    search_fields = ('machine__machine_name', 'part__part_name')

# @admin.register(Department)
# class DepartmentAdmin(admin.ModelAdmin):
#     list_display = ('department',)
#     search_fields = ('department',)

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('issue',)
    search_fields = ('issue',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_no', 'machine' ,'down_time', 'up_time', 'issue_list', 'department', 'status', 'date_created')
    search_fields = ('ticket_no', 'machine__machine_name')

@admin.register(TicketResolution)
class TicketResolutionAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'resolved_by', 'resolution_status', 'resolution_date')
    list_filter = ('resolution_status', 'resolved_by')
    search_fields = ('ticket__select_ticket', 'resolved_by__username')

