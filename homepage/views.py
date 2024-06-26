from datetime import time
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from core.models import Department, Location, Ticket, Machine, Part

# Create your views here.
def homepage(request):
    return render(request, '(homepage)/home.html')


def ticket(request):
    machines = Machine.objects.all()
    departments = Department.objects.all()
    locations = Location.objects.all()

    if request.method == 'POST':
        machine_id = request.POST['machine']
        part_ids = request.POST.getlist('parts')
        down_time_str = request.POST['down_time']
        up_time_str = request.POST['up_time'] if 'up_time' in request.POST else None
        issues = request.POST.get('issues', '')
        department_id = request.POST['department']
        location_id = request.POST['location']

        try:
            machine = get_object_or_404(Machine, id=machine_id)
            department = get_object_or_404(Department, id=department_id)
            location = get_object_or_404(Location, id=location_id)

            down_time = time.fromisoformat(down_time_str)
            up_time = time.fromisoformat(up_time_str) if up_time_str else None

            ticket = Ticket.objects.create(
                machine=machine,
                down_time=down_time,
                up_time=up_time,
                issue_list=issues,
                department=department,
                location=location
            )
            parts = Part.objects.filter(id__in=part_ids)
            ticket.parts.set(parts)
            ticket.save()

            return redirect('/')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, '(homepage)/ticket.html', {
        'machines': machines,
        'departments': departments,
        'locations': locations
    })