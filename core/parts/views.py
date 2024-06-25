from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import datetime
from core.models import Location, Part, PartPurchase
from django.utils import timezone

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

        try:
            location_id = request.POST.get('location')
            location = get_object_or_404(Location, pk=location_id)
            
            # Create and save the new part with part_warranty
            Part.objects.create(
                part_name=part_name,
                purchase_date=purchase_date,
                shelf_life=shelf_life,
                location=location,
                price=price,
                quantity=quantity,
                warranty_years=warranty_years,
                warranty_months=warranty_months
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
        "parts": parts
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
        
        part.warranty_years = int(request.POST.get('warranty_years', 0) or 0)
        part.warranty_months = int(request.POST.get('warranty_months', 0) or 0)
        part.shelf_life = request.POST.get('shelf_life')
        part.price = request.POST.get('price')
        part.quantity = request.POST.get('quantity')
        part.location = get_object_or_404(Location, pk=request.POST.get('location'))
        
        try:
            part.save()
            messages.success(request, 'Part updated successfully!')
            return redirect('parts_list')
        except Exception as e:
            messages.error(request, f'Error updating Part: {e}')
    
    context = {
        'part': part,
        'locations': Location.objects.all(),
    }
    return render(request, '(core)/parts/edit_part.html', context)

@login_required(login_url='login')
def purchase_part(request):
    if request.method == 'POST':
        part_id = request.POST.get('part_id')
        quantity = int(request.POST.get('quantity', 0))
        vendor_name = request.POST.get('vendor_name')
        gst = Decimal(request.POST.get('gst', '0.00'))
        purchase_date = timezone.now()
        part = get_object_or_404(Part, id=part_id)
        
        # Calculate total amount using Decimal for precise arithmetic
        total_amount = part.price * (1 + gst / Decimal('100')) * quantity
        
        # part.quantity += quantity
        part.save()
        
        part_purchase = PartPurchase.objects.create(
            part=part,
            vendor_name=vendor_name,
            purchase_quantity=quantity,
            gst=gst,
            total_amount=total_amount,
            purchase_date=purchase_date
        )

        messages.success(request, f"Part purchase recorded successfully: {part_purchase}")
        return redirect('dashboard')  # Replace 'part_purchase' with your view name

    locations = Location.objects.all()
    parts = Part.objects.all()
    
    context = {
        'locations': locations,
        'parts': parts
    }
    return render(request, '(core)/parts/purchase_part.html', context)

@login_required(login_url='login')
def purchase_history(request):
    purchases = PartPurchase.objects.all()
    context = {
        'purchases': purchases
    }
    return render(request, '(core)/parts/purchase_history.html', context)