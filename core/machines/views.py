from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.models import Location, Machine, MachinePart, MachinePurchase, Part
from django.utils import timezone
from decimal import Decimal
from .utils import calculate_total_amount, process_excel_data
import pandas as pd

@login_required(login_url='login')
def machines_page(request):
    return render(request, '(core)/machines/machines.html')

@login_required(login_url='login')
def add_machine(request):
    if request.method == 'POST':
        machine_name = request.POST['machine_name']
        shelf_life = request.POST['shelf_life']
        price = request.POST['price']
        quantity = request.POST['quantity']
        
        # Get purchase date from form input, defaulting to today's date if not provided
        purchase_date_str = request.POST.get('purchase_date')
        if purchase_date_str:
            purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d')
        else:
            purchase_date = timezone.now()

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
                price=price,
                quantity=quantity
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
        machine.quantity = request.POST.get('quantity')

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
    
@login_required(login_url='login')
def purchase_machine(request):
    if request.method == 'POST':
        existing_or_new = request.POST.get('existing_or_new')

        if existing_or_new == 'existing':
            machine_id = request.POST.get('machine_id')
            quantity = int(request.POST.get('quantity', 1))
            vendor_name = request.POST.get('vendor_name')
            gst = Decimal(request.POST.get('gst', '0.00'))
            purchase_date = request.POST.get('purchase_date')

            if purchase_date:
                purchase_date = timezone.datetime.strptime(purchase_date, '%Y-%m-%d').date()
            else:
                purchase_date = timezone.now().date()

            machine = get_object_or_404(Machine, pk=machine_id)
            total_amount = calculate_total_amount(machine.price, quantity, gst)

            machine_purchase = MachinePurchase.objects.create(
                machine=machine,
                vendor_name=vendor_name,
                gst=gst,
                purchase_quantity=quantity,
                total_amount=total_amount,
                purchase_date=purchase_date
            )

            messages.success(request, f"Machine purchase recorded successfully: {machine_purchase}")
            return redirect('dashboard')

        elif existing_or_new == 'new':
            new_machine_name = request.POST.get('new_machine_name')
            location_id = request.POST.get('new_machine_location')
            location = get_object_or_404(Location, pk=location_id)
            new_machine_price = Decimal(request.POST.get('new_machine_price'))
            warranty_years = int(request.POST.get('warranty_years', 0))
            warranty_months = int(request.POST.get('warranty_months', 0))
            shelf_life = request.POST.get('shelf_life')
            quantity = int(request.POST.get('quantity', 1))
            vendor_name = request.POST.get('vendor_name')
            gst = Decimal(request.POST.get('gst', '0.00'))
            purchase_date = request.POST.get('purchase_date')

            if purchase_date:
                purchase_date = timezone.datetime.strptime(purchase_date, '%Y-%m-%d').date()
            else:
                purchase_date = timezone.now().date()

            warranty_expiration_date = purchase_date + relativedelta(years=warranty_years, months=warranty_months)
            machine_warranty = warranty_expiration_date.strftime('%Y-%m-%d')

            new_machine = Machine.objects.create(
                machine_name=new_machine_name,
                location=location,
                price=new_machine_price,
                machine_warranty=machine_warranty,
                shelf_life=shelf_life,
                purchase_date=purchase_date
            )

            total_amount = calculate_total_amount(new_machine.price, quantity, gst)

            machine_purchase = MachinePurchase.objects.create(
                machine=new_machine,
                vendor_name=vendor_name,
                gst=gst,
                purchase_quantity=quantity,
                total_amount=total_amount,
                purchase_date=purchase_date
            )

            messages.success(request, f"New machine purchase recorded successfully: {machine_purchase}")
            return redirect('dashboard')

    # If request method is not POST or any other condition
    locations = Location.objects.all()
    machines = Machine.objects.all()
    context = {
        'locations': locations,
        'machines': machines
    }
    return render(request, '(core)/machines/purchase_machine.html', context)

def calculate_total_amount(price, quantity, gst):
    return price * (1 + gst / Decimal('100')) * quantity

def calculate_total_amount(price, quantity, gst):
    return price * (1 + gst / Decimal('100')) * quantity

@login_required(login_url='login')
def purchase_machine_history(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location_id = request.GET.get('location_id')
    search_query = request.GET.get('search', None)

    purchases = MachinePurchase.objects.all()

    if start_date:
        purchases = purchases.filter(purchase_date__gte=start_date)
    if end_date:
        purchases = purchases.filter(purchase_date__lte=end_date)
    if location_id:
        purchases = purchases.filter(machine__location_id=location_id)

    if search_query:
        purchases = purchases.filter(
            Q(machine__machine_name__icontains=search_query) | 
            Q(vendor_name__icontains=search_query) |
            Q(purchase_quantity__icontains=search_query) |
            Q(total_amount__icontains=search_query)
        )

    context = {
        'purchases': purchases.order_by('-purchase_date'),
        'locations': Location.objects.all()
    }
    return render(request, '(core)/machines/purchase_machine_history.html', context)