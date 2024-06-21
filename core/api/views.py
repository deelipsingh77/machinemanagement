from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from core.models import Location, Machine, MachinePart, Part

def get_parts_by_location(_, location_id):
    # Ensure the location exists
    location = get_object_or_404(Location, id=location_id)
    
    # Filter parts by the given location
    parts = Part.objects.filter(location=location).values('id', 'part_name')
    
    # Return the parts as a JSON response
    return JsonResponse(list(parts), safe=False)

def get_parts_for_machine(_, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)
    
    # Fetch parts that are mapped to the specified machine
    machine_parts = MachinePart.objects.filter(machine=machine)
    parts = Part.objects.filter(id__in=[machine_part.part.id for machine_part in machine_parts])
    
    part_list = list(parts.values('id', 'part_name'))
    return JsonResponse(part_list, safe=False)