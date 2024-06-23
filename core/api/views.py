from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404

from core.models import Location, Machine, MachinePart, Part, Ticket


def get_machines_by_location(_, location_id):
    # Ensure the location exists
    location = get_object_or_404(Location, id=location_id)

    # Filter machines by the given location
    machines = Machine.objects.filter(location=location).values("id", "machine_name")

    # Return the machines as a JSON response
    return JsonResponse(list(machines), safe=False)


def get_parts_by_location(_, location_id):
    # Ensure the location exists
    location = get_object_or_404(Location, id=location_id)

    # Filter parts by the given location
    parts = Part.objects.filter(location=location).values("id", "part_name")

    # Return the parts as a JSON response
    return JsonResponse(list(parts), safe=False)


def get_parts_for_machine(_, machine_id):
    machine = get_object_or_404(Machine, id=machine_id)

    # Fetch parts that are mapped to the specified machine
    machine_parts = MachinePart.objects.filter(machine=machine)
    parts = Part.objects.filter(
        id__in=[machine_part.part.id for machine_part in machine_parts]
    )

    part_list = list(parts.values("id", "part_name"))
    return JsonResponse(part_list, safe=False)


def get_ticket_details(_, ticket_id):
    try:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket_data = {
            "ticket_no": ticket.ticket_no,
            "machine": ticket.machine.machine_name,
            "parts": list(ticket.parts.values("id", "part_name", "quantity")),
            "down_time": ticket.down_time,
            "up_time": ticket.up_time,
            "issue": ticket.issue_list.issue,
            "remarks": ticket.remarks,
            "department": ticket.department.location,
            "status": ticket.status,
            "date_created": ticket.date_created,
        }
        return JsonResponse(ticket_data, safe=False)
    except Ticket.DoesNotExist:
        raise Http404("Ticket does not exist")