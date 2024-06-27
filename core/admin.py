from django.contrib import admin
from .models import Location, Machine, MachinePurchase, Part, MachinePart, Ticket, TicketResolution, Department, PartPurchase, UsedPart

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
    list_display = ('id', 'part_name', 'shelf_life', 'quantity', 'location', 'price', 'warranty_years', 'warranty_months')
    list_filter = ('location',)
    search_fields = ('id', 'part_name')

@admin.register(MachinePart)
class MachinePartAdmin(admin.ModelAdmin):
    list_display = ('machine', 'part', 'location')
    list_filter = ('machine', 'part')
    search_fields = ('machine__machine_name', 'part__part_name')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_no', 'machine' ,'down_time', 'up_time', 'issue_list', 'department', 'location', 'status', 'date_created')
    search_fields = ('ticket_no', 'machine__machine_name')
    filter_horizontal = ('parts',)

@admin.register(TicketResolution)
class TicketResolutionAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'resolved_by', 'resolution_status', 'resolution_date')
    list_filter = ('resolution_status', 'resolved_by')
    search_fields = ('ticket__ticket_no', 'resolved_by__username')

@admin.register(UsedPart)
class UsedPartAdmin(admin.ModelAdmin):
    list_display = ('ticket_resolution', 'part', 'quantity_used')
    list_filter = ('ticket_resolution', 'part')
    search_fields = ('ticket_resolution__ticket__ticket_no', 'part__part_name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PartPurchase)
class PartPurchaseAdmin(admin.ModelAdmin):
    list_display = ('part', 'vendor_name', 'purchase_quantity', 'gst', 'total_amount', 'purchase_date')
    list_filter = ('part', 'purchase_date')
    search_fields = ('part__part_name', 'vendor_name')

@admin.register(MachinePurchase)
class MachinePurchaseAdmin(admin.ModelAdmin):
    list_display = ('machine', 'vendor_name', 'gst', 'total_amount', 'purchase_date')
    list_filter = ('machine', 'purchase_date')
    search_fields = ('machine__machine_name', 'vendor_name')