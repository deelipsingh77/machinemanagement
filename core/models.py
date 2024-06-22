from django.db import models
from django.contrib.auth.models import User

class Machine(models.Model):
    machine_no = models.CharField(max_length=100, unique=True)
    machine_name = models.CharField(max_length=200)
    purchase_date = models.DateField()
    machine_warranty = models.DateField()
    shelf_life = models.CharField(max_length=100)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.machine_name

class Part(models.Model):
    part_no = models.CharField(max_length=100, unique=True)
    part_name = models.CharField(max_length=200)
    purchase_date = models.DateField()
    part_warranty = models.DateField()
    shelf_life = models.CharField(max_length=100)
    quantity = models.IntegerField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.part_name
    
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

# class Department(models.Model):
#     department = models.CharField(max_length=100)

#     def __str__(self):
#         return self.department
    
class Issue(models.Model):
    issue = models.CharField(max_length=100)

    def __str__(self):
        return self.issue

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
    issue_list = models.ForeignKey(Issue, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=TICKET_STATUS_CHOICES, default=PENDING)
    date_created = models.DateTimeField(auto_now_add=True)
    
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

    def __str__(self):
        return f"Resolution for Ticket {self.ticket.select_ticket} by {self.resolved_by.username}"
