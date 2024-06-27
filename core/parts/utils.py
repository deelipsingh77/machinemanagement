from core.machines.utils import parse_purchase_date
from core.models import PartPurchase
from core.models import Part, Location
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal
import pandas as pd

def process_part_excel_data(file):
    try:
        df = pd.read_excel(file)
        for index, row in df.iterrows():
            existing_or_new = row.get('existing_or_new')

            if existing_or_new == 'existing':
                part_id = row.get('part_id')
                quantity = int(row.get('quantity', 1))
                vendor_name = row.get('vendor_name')
                gst = Decimal(row.get('gst', '0.00'))
                purchase_date = row.get('purchase_date')

                if purchase_date:
                    purchase_date = parse_purchase_date(purchase_date)
                else:
                    purchase_date = timezone.now().date()

                part = get_object_or_404(Part, pk=part_id)
                total_amount = part.price * (1 + gst / Decimal('100')) * quantity
                PartPurchase.objects.create(
                    part=part,
                    vendor_name=vendor_name,
                    gst=gst,
                    purchase_quantity=quantity,
                    total_amount=total_amount,
                    purchase_date=purchase_date
                )

            elif existing_or_new == 'new':
                new_part_name = row.get('part_name')
                location_name = row.get('part_location')
                location = Location.objects.get(location=location_name)
                new_part_price = Decimal(row.get('part_price'))
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

                part = Part.objects.create(
                    part_name=new_part_name,
                    location=location,
                    price=new_part_price,
                    quantity=0,  # Initial quantity as 0
                    warranty_years=warranty_years,
                    warranty_months=warranty_months,
                    shelf_life=shelf_life
                )

                total_amount = new_part_price * (1 + gst / Decimal('100')) * quantity

                PartPurchase.objects.create(
                    part=part,
                    vendor_name=vendor_name,
                    gst=gst,
                    purchase_quantity=quantity,
                    total_amount=total_amount,
                    purchase_date=purchase_date
                )

        return True, None
    except Exception as e:
        return False, str(e)