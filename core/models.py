from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Machine(models.Model):
    machine_name = models.CharField(max_length=200)
    purchase_date = models.DateField()
    machine_warranty = models.DateField()
    shelf_life = models.CharField(max_length=100)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.machine_name

class Part(models.Model):
    part_name = models.CharField(max_length=200)
    shelf_life = models.CharField(max_length=100)
    quantity = models.IntegerField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    warranty_years = models.IntegerField(default=0, help_text="Warranty period in years")
    warranty_months = models.IntegerField(default=0, help_text="Warranty period in months")

    def __str__(self):
        return self.part_name

    def warranty_period(self):
        """Returns the warranty period in a human-readable format."""
        parts = []
        if self.warranty_years:
            parts.append(f"{self.warranty_years} yr{'s' if self.warranty_years > 1 else ''}")
        if self.warranty_months:
            parts.append(f"{self.warranty_months} month{'s' if self.warranty_months > 1 else ''}")
        return ", ".join(parts)

    def warranty_expiration_date(self, purchase_date):
        """Returns the warranty expiration date based on the purchase date."""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta

        return purchase_date + relativedelta(years=self.warranty_years, months=self.warranty_months)
    
class PartPurchase(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=200)
    purchase_quantity = models.IntegerField()
    gst = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    def save(self, *args, **kwargs):
        self.part.quantity += self.purchase_quantity
        self.part.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchased {self.purchase_quantity} of {self.part} from {self.vendor_name}"
    
class MachinePurchase(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=200)
    gst = models.DecimalField(max_digits=5, decimal_places=2)
    purchase_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Purchased {self.machine} from {self.vendor_name}"
    
class Location(models.Model):
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.location

class MachinePart(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.machine} - {self.part} at {self.location}"

class Ticket(models.Model):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    TICKET_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    ticket_no = models.CharField(max_length=100, unique=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    parts = models.ManyToManyField(Part)
    down_time = models.TimeField()
    up_time = models.TimeField(null=True, blank=True)
    issue_list = models.CharField(max_length=100, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=TICKET_STATUS_CHOICES, default=PENDING)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.ticket_no:
            self.ticket_no = self.generate_ticket_no()
        super().save(*args, **kwargs)

    def generate_ticket_no(self):
        return f"T-{uuid.uuid4().hex[:8].upper()}-{timezone.now().strftime('%Y%m%d')}"
    
    def __str__(self):
        return f"Ticket {self.ticket_no} for {self.machine}"
    
class TicketResolution(models.Model):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    TICKET_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    resolved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    resolution_date = models.DateTimeField(auto_now_add=True)
    resolution_status = models.CharField(max_length=100, choices=TICKET_STATUS_CHOICES, default=PENDING)
    remarks = models.TextField(blank=True, null=True)
    used_parts = models.ManyToManyField(Part, through='UsedPart')

    def __str__(self):
        return f"Resolution for Ticket {self.ticket.ticket_no} by {self.resolved_by.username}"

class UsedPart(models.Model):
    ticket_resolution = models.ForeignKey(TicketResolution, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity_used = models.IntegerField()

    def __str__(self):
        return f"{self.quantity_used} of {self.part} used in Ticket Resolution {self.ticket_resolution}"
