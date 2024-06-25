from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Department, Location, Ticket, Part, TicketResolution, UsedPart
from django.utils import timezone

@login_required(login_url='login')
def tickets_page(request):
    return render(request, '(core)/tickets/tickets.html')

@login_required(login_url='login')
def tickets_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        tickets = Ticket.objects.filter(
            Q(department__name__icontains=search_query) | 
            Q(ticket_no__icontains=search_query) | 
            Q(status__icontains=search_query) |
            Q(machine__machine_name__icontains=search_query) |
            Q(parts__part_name__icontains=search_query) |
            Q(down_time__icontains=search_query) |
            Q(up_time__icontains=search_query) |
            Q(issue_list__icontains=search_query) |
            Q(location_location__icontains=search_query) |
            Q(remarks__icontains=search_query)
        ).distinct()
    else:
        tickets = Ticket.objects.all().order_by('-date_created')

    # Filter tickets based on status
    filter_status = request.GET.get('status', None)
    if filter_status in ['Pending', 'In Progress', 'Completed']:
        tickets = tickets.filter(status=filter_status)

    # Filter tickets based on department
    filter_department = request.GET.get('department', None)
    if filter_department:
        tickets = tickets.filter(department__name=filter_department)

    # Filter tickets based on location
    filter_location = request.GET.get('location', None)
    if filter_location:
        tickets = tickets.filter(location__location=filter_location)

    locations = Location.objects.all()
    departments = Department.objects.all()

    context = {
        "tickets": tickets,
        "locations": locations,
        "departments": departments,
    }
    return render(request, '(core)/tickets/tickets_list.html', context)

@login_required(login_url='login')
def resolve_tickets(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        status = request.POST.get('status')

        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.status = status

        if status == Ticket.COMPLETED:
            ticket.up_time = timezone.now()  # Set up_time to current time

        ticket.save()

        # Process parts used in this resolution
        parts_used = {}
        for key, value in request.POST.items():
            if key.startswith('part_') and key.endswith('_used'):
                part_id = key.split('_')[1]
                parts_used[int(part_id)] = int(value)

        for part_id, amount_used in parts_used.items():
            if amount_used > 0:
                try:
                    part = ticket.parts.get(id=part_id)
                    if part.quantity >= amount_used:
                        part.quantity -= amount_used
                        part.save()
                        # No need to create UsedPart here; just prepare data
                    else:
                        messages.error(request, f"Not enough quantity available for part {part.part_name}. Available: {part.quantity}")
                except Part.DoesNotExist:
                    messages.error(request, f"Part {part_id} does not exist in ticket.")

        # Create a new TicketResolution entry
        ticket_resolution = TicketResolution.objects.create(
            ticket=ticket,
            resolved_by=request.user,
            resolution_status=status,
            remarks=request.POST.get('remarks', '')
        )

        # Now create UsedPart objects
        for part_id, amount_used in parts_used.items():
            if amount_used > 0:
                try:
                    part = ticket.parts.get(id=part_id)
                    UsedPart.objects.create(
                        ticket_resolution=ticket_resolution,
                        part=part,
                        quantity_used=amount_used
                    )
                except Part.DoesNotExist:
                    pass  # Handle if the part was deleted or not found

        messages.success(request, f"Ticket {ticket.ticket_no} resolved successfully.")
        return redirect('resolve_tickets')

    tickets = Ticket.objects.all()
    return render(request, '(core)/tickets/resolve_tickets.html', {'tickets': tickets})


    tickets = Ticket.objects.all()
    return render(request, '(core)/tickets/resolve_tickets.html', {'tickets': tickets})

@login_required(login_url='login')
def resolve_ticket(request, id):
    ticket = get_object_or_404(Ticket, id=id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status:
            ticket.status = status
            if status == Ticket.COMPLETED:
                ticket.up_time = timezone.now()
        
        # Validate and update parts
        parts_valid = True
        for part in ticket.parts.all():
            part_id = part.id
            amount_used = request.POST.get(f'part_{part_id}_used')
            if amount_used:
                try:
                    amount_used = int(amount_used)
                    if amount_used < 0 or amount_used > part.quantity:
                        messages.error(request, f"Invalid quantity used for part {part_id}. It should be between 0 and {part.quantity}.")
                        parts_valid = False
                    else:
                        part.quantity -= amount_used
                        part.save()
                        # No need to create UsedPart here; just prepare data
                        # Create UsedPart record after TicketResolution is created
                except ValueError:
                    messages.error(request, f"Invalid input for part {part_id}. Please enter a valid number.")
                    parts_valid = False
        
        if parts_valid:
            ticket.save()
            # Create a new TicketResolution entry
            ticket_resolution = TicketResolution.objects.create(
                ticket=ticket,
                resolved_by=request.user,
                resolution_status=status,
                remarks=request.POST.get('remarks', '')
            )
            
            # Now create UsedPart objects
            for part in ticket.parts.all():
                part_id = part.id
                amount_used = request.POST.get(f'part_{part_id}_used')
                if amount_used:
                    amount_used = int(amount_used)
                    UsedPart.objects.create(
                        ticket_resolution=ticket_resolution,
                        part=part,
                        quantity_used=amount_used
                    )
            
            messages.success(request, "Ticket resolved successfully.")
            return redirect('tickets_list')  # Replace 'tickets_list' with the name of the view to redirect to after successful resolution
    
    context = {
        'ticket': ticket,
    }
    return render(request, '(core)/tickets/resolve_ticket.html', context)
