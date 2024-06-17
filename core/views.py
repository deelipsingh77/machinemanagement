from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from core.models import Machine, Part
from django.db import models
from django.db.models import Q

@login_required(login_url='login')
def home(_):
    return redirect('dashboard')

@login_required(login_url='login')
def dashboard(request):
    # Count the total number of machines
    total_machines = Machine.objects.count()
    
    # Count the total number of parts
    total_parts = Part.objects.count()
    
    # Calculate the total value of all machines
    machines_value = Machine.objects.aggregate(total_value=models.Sum('price'))['total_value']
    machines_value = machines_value if machines_value is not None else 0
    
    # Calculate the total value of all parts
    parts_value = Part.objects.aggregate(total_value=models.Sum('price'))['total_value']
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
def add_part(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        part_number = request.POST.get('part_number')
        price = request.POST.get('price')

        Part.objects.create(name=name, description=description, part_number=part_number, price=price)
        
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