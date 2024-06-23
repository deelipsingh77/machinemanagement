from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Location, Ticket, Part, TicketResolution
from django.utils import timezone

@login_required(login_url='login')
def tickets_page(request):
    return render(request, '(core)/tickets/tickets.html')

@login_required(login_url='login')
def tickets_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        tickets = Ticket.objects.filter(
            Q(department__location__icontains=search_query) | 
            Q(ticket_no__icontains=search_query) | 
            Q(status__icontains=search_query) |
            Q(machine__machine_name__icontains=search_query) |
            Q(parts__part_name__icontains=search_query) |
            Q(down_time__icontains=search_query) |
            Q(up_time__icontains=search_query) |
            Q(issue_list__icontains=search_query) |
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
        tickets = tickets.filter(department__location=filter_department)
    
    locations = Location.objects.all()

    context = {
        "tickets": tickets,
        "locations": locations,
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

        parts_used = {key: value for key, value in request.POST.items() if key.startswith('part_') and key.endswith('_used')}
        for part_key, amount_used in parts_used.items():
            part_no = part_key.split('_')[1]
            if amount_used:  # Check if amount_used is not empty
                try:
                    part = ticket.parts.get(id=part_no)
                    part.quantity -= int(amount_used)
                    part.save()
                except Part.DoesNotExist:
                    continue

        # Create a new TicketResolution entry
        TicketResolution.objects.create(
            ticket=ticket,
            resolved_by=request.user,
            resolution_status=status,
            remarks=request.POST.get('remarks', '')
        )

        # Optionally, add a success message or redirect to another page
        return redirect('resolve_tickets')  # Redirect to the same page or another as needed

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
                ticket.uptime = timezone.now()
        
        # Validate and update parts
        parts_valid = True
        for part in ticket.parts.all():
            part_no = part.id
            amount_used = request.POST.get(f'part_{part_no}_used')
            if amount_used:
                try:
                    amount_used = int(amount_used)
                    if amount_used < 0 or amount_used > part.quantity:
                        messages.error(request, f"Invalid quantity used for part {part.id}. It should be between 0 and {part.quantity}.")
                        parts_valid = False
                    else:
                        part.quantity -= amount_used
                        part.save()
                except ValueError:
                    messages.error(request, f"Invalid input for part {part.id}. Please enter a valid number.")
                    parts_valid = False
        
        if parts_valid:
            ticket.save()
            # Create a new TicketResolution entry
            TicketResolution.objects.create(
                ticket=ticket,
                resolved_by=request.user,
                resolution_status=status,
                remarks=request.POST.get('remarks', '')
            )
            messages.success(request, "Ticket resolved successfully.")
            return redirect('tickets_list')  # Replace 'tickets_list' with the name of the view to redirect to after successful resolution
    
    context = {
        'ticket': ticket,
    }
    return render(request, '(core)/tickets/resolve_ticket.html', context)
