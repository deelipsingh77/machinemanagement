from calendar import c
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dateutil.relativedelta import relativedelta

from core.models import Location, Machine, MachinePart, Part
from django.db import models, transaction
from django.db.models import Q, Sum, F

@login_required(login_url='login')
def dashboard(request):
    # Count the total number of machines
    # total_machines = Machine.objects.count()
    
    # Count the total number of parts
    # total_parts = Part.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    # total_parts = total_parts if total_parts is not None else 0
    
    # Calculate the total value of all machines
    # machines_value = Machine.objects.aggregate(total_value=models.Sum('price'))['total_value']
    # machines_value = machines_value if machines_value is not None else 0
    
    # Calculate the total value of all parts
    # parts_value = Part.objects.annotate(
    #     total_price_per_part=F('price') * F('quantity')
    # ).aggregate(
    #     total_value=Sum('total_price_per_part')
    # )['total_value']
    # parts_value = parts_value if parts_value is not None else 0
    
    # context = {
    #     'total_machines': total_machines,
    #     'total_parts': total_parts,
    #     'machines_value': machines_value,
    #     'parts_value': parts_value,
    # }

    context = {}
    
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
        location_id = request.POST.get('location')
        
        machine = Machine.objects.get(id=machine_id)
        location = Location.objects.get(id=location_id)
        for part_id in parts_ids:
            part = Part.objects.get(id=part_id)
            MachinePart.objects.create(machine=machine, part=part, location=location)
        
        return redirect('/dashboard/')

    else:
        machines = Machine.objects.all()
        parts = Part.objects.all()
        locations = Location.objects.all()
        context = {
            'machines': machines,
            'parts': parts,
            'locations': locations,
        }
        return render(request, '(core)/machines/mapping.html', context)

@login_required(login_url='login')
def machine_mapping_list(request):
    machine_parts = MachinePart.objects.select_related('machine', 'part', 'location').all()
    machine_data = {}

    for mp in machine_parts:
        key = (mp.machine.machine_name, mp.location.location)
        if key not in machine_data:
            machine_data[key] = {
                'machine_name': mp.machine.machine_name,
                'location': mp.location.location,
                'parts': []
            }
        machine_data[key]['parts'].append(mp.part.part_name)

    return render(request, '(core)/machines/mapping_list.html', {'machine_data': machine_data.values()})

@login_required(login_url='login')
def maintenance_page(request):
    return render(request, '(core)/maintenance/maintenance.html')

@login_required(login_url='login')
def add_maintenance(request):
    # if request.method == 'POST':
    #     machine_id = request.POST.get('machine')
    #     parts_ids = request.POST.getlist('parts')
    #     description = request.POST.get('description')
    #     date = request.POST.get('date')

    #     machine = Machine.objects.get(id=machine_id)
    #     parts = Part.objects.filter(id__in=parts_ids, quantity__gt=0)
        
    #     total_cost = parts.aggregate(total_price=Sum('price'))['total_price'] or 0

    #     maintenance = Maintenance.objects.create(
    #         machine=machine,
    #         description=description,
    #         date=date,
    #         maintenance_cost=total_cost
    #     )
    #     maintenance.parts_used.set(parts)
    #     maintenance.save()

    #     for part in parts:
    #         part.quantity -= 1
    #         part.save()

    #     return redirect('maintenance_list')

    # else:
    #     machines = Machine.objects.all()
    #     parts = Part.objects.filter(quantity__gt=0)
    # context = {
    #     'machines': machines
    # }
    context = {}
    return render(request, '(core)/maintenance/add_maintenance.html')

@login_required(login_url='login')
def maintenance_list(request):
    # search_query = request.GET.get('search', '')
    # if search_query:
    #     maintenance_records = Maintenance.objects.filter(
    #         Q(machine__name__icontains=search_query) | 
    #         Q(description__icontains=search_query) | 
    #         Q(date__icontains=search_query) | 
    #         Q(maintenance_cost__icontains=search_query)
    #     ).prefetch_related('parts_used')
    # else:
    #     maintenance_records = Maintenance.objects.all().prefetch_related('parts_used')

    # # Calculate the number of parts used for each maintenance record
    # for record in maintenance_records:
    #     record.parts_count = record.parts_used.count()

    # context = {
    #     'maintenance': maintenance_records
    # }
    context = {} 
    return render(request, '(core)/maintenance/maintenance_list.html', context)

@login_required(login_url='login')
def delete_maintenance(request, id):
    # maintenance = Maintenance.objects.get(id=id)
    # maintenance.delete()
    return redirect('maintenance_list')

@login_required(login_url='login')
def edit_maintenance(request, id):
    # maintenance = Maintenance.objects.get(id=id)
    # if request.method == 'POST':
    #     machine_id = request.POST.get('machine')
    #     parts_ids = request.POST.getlist('parts')
    #     description = request.POST.get('description')
    #     date = request.POST.get('date')

    #     machine = Machine.objects.get(id=machine_id)
    #     parts = Part.objects.filter(id__in=parts_ids, quantity__gt=0)
        
    #     total_cost = parts.aggregate(total_price=Sum('price'))['total_price'] or 0

    #     with transaction.atomic():
    #         # Get the current parts associated with the maintenance record
    #         current_parts = maintenance.parts_used.all()

    #         # Increase the quantity for parts that are removed
    #         removed_parts = current_parts.exclude(id__in=parts_ids)
    #         for part in removed_parts:
    #             part.quantity += 1
    #             part.save()

    #         # Identify newly added parts
    #         current_parts_ids = current_parts.values_list('id', flat=True)
    #         newly_added_parts = parts.exclude(id__in=current_parts_ids)

    #         # Decrease the quantity for newly added parts
    #         for part in newly_added_parts:
    #             part.quantity -= 1
    #             part.save()

    #     maintenance.machine = machine
    #     maintenance.description = description
    #     maintenance.date = date
    #     maintenance.maintenance_cost = total_cost
    #     maintenance.parts_used.set(parts)
    #     maintenance.save()

    #     return redirect('maintenance_list')

    # else:
    #     machines = Machine.objects.all()
    #     parts = Part.objects.filter(quantity__gt=0)
    context = {}
    return render(request, '(core)/maintenance/edit_maintenance.html', context)
    