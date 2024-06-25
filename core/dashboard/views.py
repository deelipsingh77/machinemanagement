from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q
from django.core.paginator import Paginator
from core.models import Machine, Part, PartPurchase, Ticket, Location

@login_required(login_url='login')
def dashboard(request):
    # Count the total number of parts
    total_parts = Part.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    total_parts = total_parts if total_parts is not None else 0
    
    # Calculate the total value of all machines
    machines_value = Machine.objects.aggregate(total_value=Sum('price'))['total_value']
    machines_value = machines_value if machines_value is not None else 0
    
    # Calculate the total value of all parts
    parts_value = Part.objects.annotate(
        total_price_per_part=F('price') * F('quantity')
    ).aggregate(
        total_value=Sum('total_price_per_part')
    )['total_value']
    parts_value = parts_value if parts_value is not None else 0

    # Calculate the total value of all parts purchased
    total_purchased_value = PartPurchase.objects.aggregate(total_purchased_value=Sum('total_amount'))['total_purchased_value']
    total_purchased_value = total_purchased_value if total_purchased_value is not None else 0
    
    # Count tickets based on status
    pending_tickets_count = Ticket.objects.filter(status='Pending').count()
    in_progress_tickets_count = Ticket.objects.filter(status='In Progress').count()
    completed_tickets_count = Ticket.objects.filter(status='Completed').count()
    
    # Retrieve all tickets and order by date_created
    tickets = Ticket.objects.all().order_by('-date_created')
    
    # Filter tickets based on search query
    search_query = request.GET.get('search', None)
    if search_query:
        tickets = tickets.filter(
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
    
    # Filter tickets based on status
    filter_status = request.GET.get('status', None)
    if filter_status in ['Pending', 'In Progress', 'Completed']:
        tickets = tickets.filter(status=filter_status)

    # Filter tickets based on department
    filter_department = request.GET.get('department', None)
    if filter_department:
        tickets = tickets.filter(department__location=filter_department)
    
    # Pagination setup for tickets
    paginator = Paginator(tickets, 10)  # Show 10 tickets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    total_machines = Machine.objects.count()
    locations = Location.objects.all()
    
    context = {
        "total_machines": total_machines,
        "total_parts": total_parts,
        'machines_value': machines_value,
        'parts_value': parts_value,
        'total_purchased_value': total_purchased_value,
        'pending_tickets_count': pending_tickets_count,
        'in_progress_tickets_count': in_progress_tickets_count,
        'completed_tickets_count': completed_tickets_count,
        'tickets': page_obj,
        'locations': locations,
    }
    
    return render(request, '(core)/dashboard.html', context)