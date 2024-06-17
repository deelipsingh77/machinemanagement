from django.db import models

class Machine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    part_number = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Maintenance(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    parts_used = models.ManyToManyField(Part)
    description = models.TextField()
    date = models.DateField()
    maintenance_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.machine.name} - {self.date}"
