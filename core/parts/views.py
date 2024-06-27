from decimal import Decimal
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from core.models import ExcelFile, Location, Part, PartPurchase
from django.utils import timezone

from core.parts.utils import process_part_excel_data

@login_required(login_url='login')
def parts_page(request):
    return render(request, '(core)/parts/parts.html')

@login_required(login_url='login')
def add_part(request):
    if request.method == 'POST':
        part_name = request.POST.get('part_name')
        warranty_years = int(request.POST.get('warranty_years', 0) or 0)
        warranty_months = int(request.POST.get('warranty_months', 0) or 0)
        shelf_life = request.POST.get('shelf_life')
        price = request.POST.get('price')
        quantity = int(request.POST.get('quantity', 1) or 1)

        try:
            location_id = request.POST.get('location')
            location = get_object_or_404(Location, pk=location_id)
            
            # Create and save the new part with part_warranty
            Part.objects.create(
                part_name=part_name,
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
        if 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            obj = ExcelFile.objects.create(file=excel_file)
            file_path = obj.file.path
            success, message = process_part_excel_data(file_path)
            os.remove(file_path)
            obj.delete()
            if success:
                messages.success(request, 'Excel file processed successfully.')
            else:
                messages.error(request, f"Error processing Excel file: {message}")
            return redirect('purchase_history')

        existing_or_new = request.POST.get('existing_or_new')
        quantity = int(request.POST.get('quantity', 0))
        vendor_name = request.POST.get('vendor_name')
        gst = Decimal(request.POST.get('gst', '0.00'))
        purchase_date = request.POST.get('purchase_date')

        if purchase_date:
            purchase_date = timezone.datetime.strptime(purchase_date, '%Y-%m-%d').date()
        else:
            purchase_date = timezone.now().date()

        if existing_or_new == 'existing':
            part_id = request.POST.get('part_id')
            part = get_object_or_404(Part, id=part_id)
            total_amount = part.price * (1 + gst / Decimal('100')) * quantity
        else:
            new_part_name = request.POST.get('new_part_name')
            new_part_location = request.POST.get('new_part_location')
            warranty_years = int(request.POST.get('warranty_years', 0) or 0)
            warranty_months = int(request.POST.get('warranty_months', 0) or 0)
            shelf_life = request.POST.get('shelf_life')
            new_part_price = Decimal(request.POST.get('new_part_price'))

            location = get_object_or_404(Location, pk=new_part_location)

            part = Part.objects.create(
                part_name=new_part_name,
                location=location,
                price=new_part_price,
                quantity=0,  # Initial quantity as 0
                warranty_years=warranty_years,
                warranty_months=warranty_months,
                shelf_life=int(shelf_life)
            )
            total_amount = new_part_price * (1 + gst / Decimal('100')) * quantity

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
        return redirect('purchase_history')

    locations = Location.objects.all()
    parts = Part.objects.all()

    context = {
        'locations': locations,
        'parts': parts
    }
    return render(request, '(core)/parts/purchase_part.html', context)

@login_required(login_url='login')
def purchase_history(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location_id = request.GET.get('location_id')
    search_query = request.GET.get('search', None)

    purchases = PartPurchase.objects.all()

    if start_date:
        purchases = purchases.filter(purchase_date__gte=start_date)
    if end_date:
        purchases = purchases.filter(purchase_date__lte=end_date)
    if location_id:
        purchases = purchases.filter(part__location_id=location_id)

    if search_query:
        purchases = purchases.filter(
            Q(part__part_name__icontains=search_query) | 
            Q(vendor_name__icontains=search_query) |
            Q(purchase_quantity__icontains=search_query) |
            Q(total_amount__icontains=search_query)
        )

    context = {
        'purchases': purchases.order_by('-purchase_date'),
        'locations': Location.objects.all()
    }
    return render(request, '(core)/parts/purchase_history.html', context)
