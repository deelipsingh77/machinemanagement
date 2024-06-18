from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from core.models import Machine, Maintenance, Part
from django.db import models, transaction
from django.db.models import Q, Sum, F

@login_required(login_url='login')
def home(_):
    return redirect('dashboard')

@login_required(login_url='login')
def dashboard(request):
    # Count the total number of machines
    total_machines = Machine.objects.count()
    
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
    
    context = {
        'total_machines': total_machines,
        'total_parts': total_parts,
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
        name = request.POST['name']
        description = request.POST['description']
        serial_number = request.POST['serial_number']
        price = request.POST['price']
        
        Machine.objects.create(name=name, description=description, serial_number=serial_number, price=price) 
        
        return redirect('machines_list')
    return render(request, '(core)/machines/add_machine.html')

@login_required(login_url='login')
def machines_list(request):
    search_query = request.GET.get('search', '')  # Get the search parameter from the URL
    if search_query:
        machines = Machine.objects.filter(
            Q(name__icontains=search_query) | 
            Q(serial_number__icontains=search_query) | 
            Q(price__icontains=search_query)
        )
    else:
        machines = Machine.objects.all()
    return render(request, '(core)/machines/machines_list.html', {'machines': machines})


@login_required(login_url='login')
def delete_machine(request, id):
    machine = Machine.objects.get(id=id)
    machine.delete()
    return redirect('machines_list')

@login_required(login_url='login')
def edit_machine(request, id):
    machine = Machine.objects.get(id=id)
    if request.method == 'POST':
        machine.name = request.POST.get('name')
        machine.description = request.POST.get('description')
        machine.serial_number = request.POST.get('serial_number')
        machine.price = request.POST.get('price')
        machine.quantity = request.POST.get('quantity')
        machine.save()
        return redirect('machines_list')
    return render(request, '(core)/machines/edit_machine.html', {'machine': machine})


@login_required(login_url='login')
def add_part(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        part_number = request.POST.get('part_number')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')

        Part.objects.create(name=name, description=description, part_number=part_number, price=price, quantity=int(quantity))
        
        return redirect('parts_list')
    return render(request, '(core)/parts/add_part.html')


@login_required(login_url='login')
def parts_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        parts = Part.objects.filter(
            Q(name__icontains=search_query) | 
            Q(part_number__icontains=search_query) | 
            Q(price__icontains=search_query)
        )
    else:
        parts = Part.objects.all()
    return render(request, '(core)/parts/parts_list.html', {'parts': parts})

@login_required(login_url='login')
def delete_part(request, id):
    part = Part.objects.get(id=id)
    part.delete()
    return redirect('parts_list')

@login_required(login_url='login')
def edit_part(request, id):
    part = Part.objects.get(id=id)
    if request.method == 'POST':
        part.name = request.POST.get('name')
        part.description = request.POST.get('description')
        part.part_number = request.POST.get('part_number')
        part.price = request.POST.get('price')
        part.quantity = request.POST.get('quantity')
        part.save()
        return redirect('parts_list')
    return render(request, '(core)/parts/edit_part.html', {'part': part})

@login_required(login_url='login')
def maintenance_page(request):
    return render(request, '(core)/maintenance/maintenance.html')

@login_required(login_url='login')
def add_maintenance(request):
    if request.method == 'POST':
        machine_id = request.POST.get('machine')
        parts_ids = request.POST.getlist('parts')
        description = request.POST.get('description')
        date = request.POST.get('date')

        machine = Machine.objects.get(id=machine_id)
        parts = Part.objects.filter(id__in=parts_ids, quantity__gt=0)
        
        total_cost = parts.aggregate(total_price=Sum('price'))['total_price'] or 0

        maintenance = Maintenance.objects.create(
            machine=machine,
            description=description,
            date=date,
            maintenance_cost=total_cost
        )
        maintenance.parts_used.set(parts)
        maintenance.save()

        for part in parts:
            part.quantity -= 1
            part.save()

        return redirect('maintenance_list')

    else:
        machines = Machine.objects.all()
        parts = Part.objects.filter(quantity__gt=0)
        return render(request, '(core)/maintenance/add_maintenance.html', {'machines': machines, 'parts': parts})

@login_required(login_url='login')
def maintenance_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        maintenance_records = Maintenance.objects.filter(
            Q(machine__name__icontains=search_query) | 
            Q(description__icontains=search_query) | 
            Q(date__icontains=search_query) | 
            Q(maintenance_cost__icontains=search_query)
        ).prefetch_related('parts_used')
    else:
        maintenance_records = Maintenance.objects.all().prefetch_related('parts_used')

    # Calculate the number of parts used for each maintenance record
    for record in maintenance_records:
        record.parts_count = record.parts_used.count()

    return render(request, '(core)/maintenance/maintenance_list.html', {'maintenance': maintenance_records})

@login_required(login_url='login')
def delete_maintenance(request, id):
    maintenance = Maintenance.objects.get(id=id)
    maintenance.delete()
    return redirect('maintenance_list')

@login_required(login_url='login')
def edit_maintenance(request, id):
    maintenance = Maintenance.objects.get(id=id)
    if request.method == 'POST':
        machine_id = request.POST.get('machine')
        parts_ids = request.POST.getlist('parts')
        description = request.POST.get('description')
        date = request.POST.get('date')

        machine = Machine.objects.get(id=machine_id)
        parts = Part.objects.filter(id__in=parts_ids, quantity__gt=0)
        
        total_cost = parts.aggregate(total_price=Sum('price'))['total_price'] or 0

        with transaction.atomic():
            # Get the current parts associated with the maintenance record
            current_parts = maintenance.parts_used.all()

            # Increase the quantity for parts that are removed
            removed_parts = current_parts.exclude(id__in=parts_ids)
            for part in removed_parts:
                part.quantity += 1
                part.save()

            # Identify newly added parts
            current_parts_ids = current_parts.values_list('id', flat=True)
            newly_added_parts = parts.exclude(id__in=current_parts_ids)

            # Decrease the quantity for newly added parts
            for part in newly_added_parts:
                part.quantity -= 1
                part.save()

        maintenance.machine = machine
        maintenance.description = description
        maintenance.date = date
        maintenance.maintenance_cost = total_cost
        maintenance.parts_used.set(parts)
        maintenance.save()

        return redirect('maintenance_list')

    else:
        machines = Machine.objects.all()
        parts = Part.objects.filter(quantity__gt=0)
        return render(request, '(core)/maintenance/edit_maintenance.html', {'maintenance': maintenance, 'machines': machines, 'parts': parts})
    