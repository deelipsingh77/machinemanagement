from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.models import Location, Machine, MachinePart, Part

@login_required(login_url='login')
def machines_page(request):
    return render(request, '(core)/machines/machines.html')

@login_required(login_url='login')
def add_machine(request):
    if request.method == 'POST':
        machine_name = request.POST['machine_name']
        shelf_life = request.POST['shelf_life']
        price = request.POST['price']
        
        purchase_date = datetime.strptime(request.POST['purchase_date'], '%Y-%m-%d')
        warranty_years = int(request.POST.get('warranty_years', 0) or 0)
        warranty_months = int(request.POST.get('warranty_months', 0) or 0)

        warranty_expiration_date = purchase_date + relativedelta(years=warranty_years, months=warranty_months)
        machine_warranty = warranty_expiration_date.strftime('%Y-%m-%d')

        try:
            location_id = request.POST.get('location')
            location = get_object_or_404(Location, pk=location_id)
            
            Machine.objects.create(
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
            Q(id__icontains=search_query) | 
            Q(price__icontains=search_query) |
            Q(location__location__icontains=search_query)
        )
    else:
        machines = Machine.objects.all()
    context = {
        'machines': machines
    }
    return render(request, '(core)/machines/machines_list.html', context)


@login_required(login_url='login')
def delete_machine(_, id):
    machine = get_object_or_404(Machine, id=id)
    machine.delete()
    return redirect('machines_list')

@login_required(login_url='login')
def edit_machine(request, id):
    machine = get_object_or_404(Machine, id=id)
    
    if request.method == 'POST':
        machine.machine_name = request.POST.get('machine_name')
        machine.shelf_life = request.POST.get('shelf_life')
        machine.price = request.POST.get('price')

        purchase_date = datetime.strptime(request.POST.get('purchase_date'), '%Y-%m-%d')
        warranty_years = int(request.POST.get('warranty_years', 0) or 0)
        warranty_months = int(request.POST.get('warranty_months', 0) or 0)

        warranty_expiration_date = purchase_date + relativedelta(years=warranty_years, months=warranty_months)
        machine.machine_warranty = warranty_expiration_date.strftime('%Y-%m-%d')

        location_id = request.POST.get('location')
        location = get_object_or_404(Location, pk=location_id)
        machine.location = location
        
        machine.purchase_date = purchase_date

        try:
            machine.save()
            messages.success(request, 'Machine updated successfully!')
            return redirect('machines_list')
        except Exception as e:
            messages.error(request, f'Error updating machine: {e}')
    
    context = {
        'machine': machine,
        'locations': Location.objects.all()
    }
    return render(request, '(core)/machines/edit_machine.html', context)

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
    