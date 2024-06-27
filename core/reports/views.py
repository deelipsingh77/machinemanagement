from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from django.utils.dateparse import parse_date
from core.models import Machine, Location, Part, PartPurchase
from datetime import datetime
from core.models import UsedPart

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

@login_required(login_url='login')
def daily_part_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        start_date = None
        end_date = None

    parts = Part.objects.all()
    report_data = []

    for part in parts:
        # Calculate Opening Quantity
        if start_date:
            total_used = UsedPart.objects.filter(part=part, ticket_resolution__resolution_date__date__lt=start_date).aggregate(total=Sum('quantity_used'))['total']
            total_purchased = PartPurchase.objects.filter(part=part, purchase_date__lt=start_date).aggregate(total=Sum('purchase_quantity'))['total']

            used_quantity = total_used if total_used is not None else 0
            purchased_quantity = total_purchased if total_purchased is not None else 0

            opening_quantity = part.quantity - used_quantity + purchased_quantity
        else:
            opening_quantity = part.quantity

        # Calculate Purchase Quantity and Issue Quantity within the date range
        if start_date and end_date:
            purchase_quantity = PartPurchase.objects.filter(part=part, purchase_date__range=[start_date, end_date]).aggregate(total=Sum('purchase_quantity'))['total'] or 0
            issue_quantity = UsedPart.objects.filter(part=part, ticket_resolution__resolution_date__date__range=[start_date, end_date]).aggregate(total=Sum('quantity_used'))['total'] or 0
        else:
            purchase_quantity = PartPurchase.objects.filter(part=part).aggregate(total=Sum('purchase_quantity'))['total'] or 0
            issue_quantity = UsedPart.objects.filter(part=part).aggregate(total=Sum('quantity_used'))['total'] or 0

        # Calculate Closing Balance
        closing_balance = opening_quantity + purchase_quantity - issue_quantity

        report_data.append({
            'part_name': part.part_name,
            'opening_quantity': opening_quantity,
            'purchase_quantity': purchase_quantity,
            'issue_quantity': issue_quantity,
            'closing_balance': closing_balance
        })

    context = {
        'report_data': report_data,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, '(core)/reports/daily_part_report.html', context)
