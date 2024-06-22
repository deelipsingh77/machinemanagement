from calendar import c
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from core.models import Location, Machine, MachinePart, Part, Ticket, TicketResolution
from django.db import models, transaction
from django.db.models import Q, Sum, F

@login_required(login_url='login')
def dashboard(request):
    # Count the total number of machines
    # total_machines = Machine.objects.count()
    
    # Count the total number of parts
    total_parts = Part.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    total_parts = total_parts if total_parts is not None else 0
    
    # Calculate the total value of all machines
    machines_value = Machine.objects.aggregate(total_value=models.Sum('price'))['total_value']
    machines_value = machines_value if machines_value is not None else 0
    
    # Calculate the total value of all parts
    parts_value = Part.objects.annotate(
        total_price_per_part=F('price') * F('quantity')
    ).aggregate(
        total_value=Sum('total_price_per_part')
    )['total_value']
    parts_value = parts_value if parts_value is not None else 0
    
    total_machines = Machine.objects.count()
    context = {
        "total_machines": total_machines,
        "total_parts": total_parts,
        'machines_value': machines_value,
        'parts_value': parts_value,
    }
    
    return render(request, '(core)/dashboard.html', context)

@login_required(login_url='login')
def machines_page(request):
    return render(request, '(core)/machines/machines.html')

@login_required(login_url='login')
def parts_page(request):
    return render(request, '(core)/parts/parts.html')

@login_required(login_url='login')
def add_machine(request):
    if request.method == 'POST':
        machine_no = request.POST['machine_no']
        machine_name = request.POST['machine_name']
        shelf_life = request.POST['shelf_life']
        price = request.POST['price']
        
        purchase_date = datetime.strptime(request.POST['purchase_date'], '%Y-%m-%d')
        warranty_years = int(request.POST.get('warranty_years', 0) or 0)  # Assuming input field is named 'warranty_years'
        warranty_months = int(request.POST.get('warranty_months', 0) or 0)  # Assuming input field is named 'warranty_months'

        # Calculate warranty expiration date
        warranty_expiration_date = purchase_date + relativedelta(years=warranty_years, months=warranty_months)

        # Convert warranty_expiration_date to string format if necessary
        machine_warranty = warranty_expiration_date.strftime('%Y-%m-%d')

        try:
            location_id = request.POST.get('location')
            location = get_object_or_404(Location, pk=location_id)
            
            Machine.objects.create(
                machine_no=machine_no,
                machine_name=machine_name,
                purchase_date=purchase_date,
                machine_warranty=machine_warranty,
                shelf_life=shelf_life,
                location=location,
                price=price
            )
            messages.success(request, 'Machine added successfully!')
            return redirect('machines_list')
        except Exception as e:
            messages.error(request, f'Error adding machine: {e}')

    return render(request, '(core)/machines/add_machine.html', {'locations': Location.objects.all()})

@login_required(login_url='login')
def machines_list(request):
    search_query = request.GET.get('search', '')  # Get the search parameter from the URL
    if search_query:
        machines = Machine.objects.filter(
            Q(machine_name__icontains=search_query) | 
            Q(machine_no__icontains=search_query) | 
            Q(price__icontains=search_query)
        )
    else:
        machines = Machine.objects.all()
    context = {
        'machines': machines
    }
    return render(request, '(core)/machines/machines_list.html', context)


@login_required(login_url='login')
def delete_machine(request, id):
    # machine = Machine.objects.get(id=id)
    # machine.delete()
    return redirect('machines_list')

@login_required(login_url='login')
def edit_machine(request, id):
    # machine = Machine.objects.get(id=id)
    # if request.method == 'POST':
    #     machine.name = request.POST.get('name')
    #     machine.description = request.POST.get('description')
    #     machine.serial_number = request.POST.get('serial_number')
    #     machine.price = request.POST.get('price')
    #     machine.quantity = request.POST.get('quantity')
    #     machine.save()
    #     return redirect('machines_list')
    # context = {
    #     'machine': machine
    # }
    context = {}
    return render(request, '(core)/machines/edit_machine.html', context)


@login_required(login_url='login')
def add_part(request):
    if request.method == 'POST':
        part_no = request.POST.get('part_no')
        part_name = request.POST.get('part_name')
        purchase_date_str = request.POST.get('purchase_date')
        warranty_years = int(request.POST.get('warranty_years', 0) or 0)
        warranty_months = int(request.POST.get('warranty_months', 0) or 0)
        shelf_life = request.POST.get('shelf_life')
        price = request.POST.get('price')
        quantity = int(request.POST.get('quantity',1) or 1)

        # Convert purchase_date from string to date object
        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()

        # Calculate part_warranty by adding warranty_years and warranty_months to purchase_date
        part_warranty = purchase_date + relativedelta(years=warranty_years, months=warranty_months)

        
        try:
            location_id = request.POST.get('location')
            location = get_object_or_404(Location, pk=location_id)
            
            # Create and save the new part with part_warranty
            Part.objects.create(
                part_no=part_no,
                part_name=part_name,
                purchase_date=purchase_date,
                part_warranty=part_warranty,
                shelf_life=shelf_life,
                location=location,
                price=price,
                quantity=int(quantity)
            )
            messages.success(request, 'Part added successfully!')
            return redirect('parts_list')
        except Exception as e:
            messages.error(request, f'Error adding Part: {e}')
            
        
    return render(request, '(core)/parts/add_part.html', {'locations': Location.objects.all()})


@login_required(login_url='login')
def parts_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        parts = Part.objects.filter(
            Q(part_name__icontains=search_query) | 
            Q(part_no__icontains=search_query) | 
            Q(price__icontains=search_query)
        )
    else:
        parts = Part.objects.all()
    context = {
        'parts': parts
    }
    return render(request, '(core)/parts/parts_list.html', context)

@login_required(login_url='login')
def delete_part(request, id):
    # part = Part.objects.get(id=id)
    # part.delete()
    return redirect('parts_list')

@login_required(login_url='login')
def edit_part(request, id):
    # part = Part.objects.get(id=id)
    # if request.method == 'POST':
    #     part.name = request.POST.get('name')
    #     part.description = request.POST.get('description')
    #     part.part_number = request.POST.get('part_number')
    #     part.price = request.POST.get('price')
    #     part.quantity = request.POST.get('quantity')
    #     part.save()
    #     return redirect('parts_list')

    # context = {
    #     'part': part
    # }
    context = {}
    return render(request, '(core)/parts/edit_part.html')

@login_required(login_url='login')
def machine_mapping(request):
    if request.method == 'POST':
        machine_id = request.POST.get('machine')
        parts_ids = request.POST.getlist('part')
        # location_id = request.POST.get('location')
        
        machine = Machine.objects.get(id=machine_id)
        # location = Location.objects.get(id=location_id)
        for part_id in parts_ids:
            part = Part.objects.get(id=part_id)
            MachinePart.objects.create(machine=machine, part=part, location=machine.location)
        
        return redirect('mapping_list')

    else:
        machines = Machine.objects.all()
        parts = Part.objects.all()
        locations = Location.objects.all()
        context = {
            'machines': machines,
            'parts': parts,
            # 'locations': locations,
        }
        return render(request, '(core)/machines/mapping.html', context)

@login_required(login_url='login')
def machine_mapping_list(request):
    machines = Machine.objects.all()
    return render(request, '(core)/machines/mapping_list.html', {
        'machines': machines,
    })

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
            Q(issue_list__issue__icontains=search_query) |
            Q(remarks__icontains=search_query)
        ).distinct()
    else:
        tickets = Ticket.objects.all().order_by('-date_created')
    context = {
        "tickets": tickets
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
                    part = ticket.parts.get(part_no=part_no)
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
            part_no = part.part_no
            amount_used = request.POST.get(f'part_{part_no}_used')
            if amount_used:
                try:
                    amount_used = int(amount_used)
                    if amount_used < 0 or amount_used > part.quantity:
                        messages.error(request, f"Invalid amount used for part {part.part_no}. It should be between 0 and {part.quantity}.")
                        parts_valid = False
                    else:
                        part.quantity -= amount_used
                        part.save()
                except ValueError:
                    messages.error(request, f"Invalid input for part {part.part_no}. Please enter a valid number.")
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
