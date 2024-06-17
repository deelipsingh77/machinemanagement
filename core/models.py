from django.db import models

class Machine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField()

    # Many-to-many relationship with Machine
    machines = models.ManyToManyField(Machine, related_name='parts')

    def __str__(self):
        return self.name

class MaintenanceTask(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='maintenance_tasks')
    task_name = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.machine.name} - {self.task_name}"

    class Meta:
        ordering = ['-scheduled_date']

