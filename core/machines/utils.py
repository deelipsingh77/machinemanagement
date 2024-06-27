from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from core.models import Machine, MachinePurchase, Location
import pandas as pd
from datetime import datetime

# Function to calculate total amount
def calculate_total_amount(price, quantity, gst):
    return price * (1 + gst / Decimal('100')) * quantity

def process_excel_data(file):
    try:
        df = pd.read_excel(file)
        for index, row in df.iterrows():
            existing_or_new = row.get('existing_or_new')

            if existing_or_new == 'existing':
                machine_id = row.get('machine_id')
                quantity = int(row.get('quantity', 1))
                vendor_name = row.get('vendor_name')
                gst = Decimal(row.get('gst', '0.00'))
                purchase_date = row.get('purchase_date')

                if purchase_date:
                    purchase_date = parse_purchase_date(purchase_date)
                else:
                    purchase_date = timezone.now().date()

                machine = get_object_or_404(Machine, pk=machine_id)
                total_amount = calculate_total_amount(machine.price, quantity, gst)
                print(machine_id, quantity, vendor_name, gst, purchase_date, total_amount, machine)
                MachinePurchase.objects.create(
                    machine=machine,
                    vendor_name=vendor_name,
                    gst=gst,
                    purchase_quantity=quantity,
                    total_amount=total_amount,
                    purchase_date=purchase_date
                )

            elif existing_or_new == 'new':
                new_machine_name = row.get('machine_name')
                location_name = row.get('machine_location')
                location = Location.objects.get(location=location_name)
                new_machine_price = Decimal(row.get('machine_price'))
                warranty_years = int(row.get('warranty_years', 0))
                warranty_months = int(row.get('warranty_months', 0))
                shelf_life = row.get('shelf_life')
                quantity = int(row.get('quantity', 1))
                vendor_name = row.get('vendor_name')
                gst = Decimal(row.get('gst', '0.00'))
                purchase_date = row.get('purchase_date')

                if purchase_date:
                    purchase_date = parse_purchase_date(purchase_date)
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

                MachinePurchase.objects.create(
                    machine=new_machine,
                    vendor_name=vendor_name,
                    gst=gst,
                    purchase_quantity=quantity,
                    total_amount=total_amount,
                    purchase_date=purchase_date
                )

        return True, None
    except Exception as e:
        return False, str(e)

def parse_purchase_date(purchase_date):
    if isinstance(purchase_date, datetime):
        return purchase_date.date()
    elif isinstance(purchase_date, str):
        try:
            return datetime.strptime(purchase_date, '%Y-%m-%d').date()
        except ValueError:
            try:
                return datetime.strptime(purchase_date, '%Y-%m-%d %H:%M:%S').date()
            except ValueError:
                raise ValueError("Date format is not recognized")
    else:
        raise ValueError("Unsupported date format")