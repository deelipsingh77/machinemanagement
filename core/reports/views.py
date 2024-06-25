from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils.dateparse import parse_date
from core.models import Machine, Location, Part, PartPurchase
from django.db.models import Q

@login_required(login_url='login')
def reports(request):
    return render(request, '(core)/reports/reports.html')

@login_required(login_url='login')
def machines_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location_id = request.GET.get('location_id')

    machines = Machine.objects.all()

    if start_date:
        machines = machines.filter(purchase_date__gte=start_date)
    if end_date:
        machines = machines.filter(purchase_date__lte=end_date)
    if location_id:
        machines = machines.filter(location_id=location_id)

    total_value = machines.aggregate(total_value=Sum('price'))['total_value'] or 0

    locations = Location.objects.all()

    context = {
        'machines': machines,
        'total_value': total_value,
        'locations': locations,
        'start_date': start_date,
        'end_date': end_date,
        'location_id': location_id,
    }

    return render(request, '(core)/reports/machines_report.html', context)

@login_required(login_url='login')
def parts_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location_id = request.GET.get('location_id')

    parts = Part.objects.all()

    total_value = parts.aggregate(total_value=Sum('price'))['total_value'] or 0
    total_quantity = parts.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    locations = Location.objects.all()

    context = {
        'parts': parts,
        'total_value': total_value,
        'total_quantity': total_quantity,
        'locations': locations,
        'start_date': start_date,
        'end_date': end_date,
        'location_id': location_id,
    }

    return render(request, '(core)/reports/parts_report.html', context)

@login_required(login_url='login')
def purchases_report(request):
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

    total_value = purchases.aggregate(total_value=Sum('total_amount'))['total_value'] or 0
    total_quantity = purchases.aggregate(total_quantity=Sum('purchase_quantity'))['total_quantity'] or 0

    locations = Location.objects.all()

    context = {
        'purchases': purchases,
        'total_value': total_value,
        'total_quantity': total_quantity,
        'locations': locations,
        'start_date': start_date,
        'end_date': end_date,
        'location_id': location_id,
    }

    return render(request, '(core)/reports/purchases_report.html', context)
