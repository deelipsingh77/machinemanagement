from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.models import Location, Part
from django.utils.timezone import make_aware

@login_required(login_url='login')
def parts_page(request):
    return render(request, '(core)/parts/parts.html')

@login_required(login_url='login')
def add_part(request):
    if request.method == 'POST':
        part_name = request.POST.get('part_name')
        purchase_date_str = request.POST.get('purchase_date')
        warranty_years = int(request.POST.get('warranty_years', 0) or 0)
        warranty_months = int(request.POST.get('warranty_months', 0) or 0)
        shelf_life = request.POST.get('shelf_life')
        price = request.POST.get('price')
        quantity = int(request.POST.get('quantity', 1) or 1)

        # Convert purchase_date from string to date object
        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()

        # Calculate part_warranty by adding warranty_years and warranty_months to purchase_date
        part_warranty = purchase_date + relativedelta(years=warranty_years, months=warranty_months)

        try:
            location_id = request.POST.get('location')
            location = get_object_or_404(Location, pk=location_id)
            
            # Create and save the new part with part_warranty
            Part.objects.create(
                part_name=part_name,
                purchase_date=purchase_date,
                part_warranty=part_warranty,
                shelf_life=shelf_life,
                location=location,
                price=price,
                quantity=quantity
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
            Q(price__icontains=search_query) |
            Q(location__location__icontains=search_query)
        )
    else:
        parts = Part.objects.all()
    context = {
        'parts': parts
    }
    return render(request, '(core)/parts/parts_list.html', context)

@login_required(login_url='login')
def delete_part(request, id):
    part = get_object_or_404(Part, id=id)
    part.delete()
    messages.success(request, 'Part deleted successfully!')
    return redirect('parts_list')

@login_required(login_url='login')
def edit_part(request, id):
    part = get_object_or_404(Part, id=id)
    
    if request.method == 'POST':
        part.part_name = request.POST.get('part_name')
        
        # Ensure purchase_date is handled correctly
        purchase_date_str = request.POST.get('purchase_date')
        try:
            part.purchase_date = make_aware(datetime.strptime(purchase_date_str, '%Y-%m-%d'))
        except ValueError:
            part.purchase_date = None
        
        warranty_years = int(request.POST.get('warranty_years', 0) or 0)
        warranty_months = int(request.POST.get('warranty_months', 0) or 0)
        
        # Calculate warranty end date
        if part.purchase_date:
            warranty_end_date = part.purchase_date + relativedelta(years=warranty_years, months=warranty_months)
            part.part_warranty = warranty_end_date
        else:
            part.part_warranty = None
        
        part.shelf_life = request.POST.get('shelf_life')
        part.price = request.POST.get('price')
        part.quantity = request.POST.get('quantity')
        part.location_id = request.POST.get('location')
        
        try:
            part.save()
            messages.success(request, 'Part updated successfully!')
            return redirect('parts_list')
        except Exception as e:
            messages.error(request, f'Error updating Part: {e}')
    
    # Calculate warranty years and months based on current date
    warranty_years = 0
    warranty_months = 0
    warranty_end_date = part.part_warranty
    
    if part.purchase_date and warranty_end_date:
        delta = warranty_end_date - part.purchase_date
        warranty_years = delta.days // 365
        warranty_months = (delta.days % 365) // 30  # Approximate calculation for months
    
    context = {
        'part': part,
        'locations': Location.objects.all(),
        'warranty_years': warranty_years,
        'warranty_months': warranty_months,
    }
    return render(request, '(core)/parts/edit_part.html', context)