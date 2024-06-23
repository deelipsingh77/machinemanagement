from datetime import time
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from core.models import Location, Ticket, Machine, Part, Issue

# Create your views here.
def homepage(request):
    return render(request, '(homepage)/home.html')


def ticket(request):
    machines = Machine.objects.all()
    issues = Issue.objects.all()
    departments = Location.objects.all()

    if request.method == 'POST':
        machine_id = request.POST['machine']
        part_ids = request.POST.getlist('parts')
        down_time_str = request.POST['down_time']
        up_time_str = request.POST['up_time'] if 'up_time' in request.POST else None
        issue_id = request.POST['issue_list']
        remarks = request.POST.get('remarks', '')
        department_id = request.POST['department']

        try:
            machine = get_object_or_404(Machine, id=machine_id)
            issue = get_object_or_404(Issue, id=issue_id)
            department = get_object_or_404(Location, id=department_id)

            down_time = time.fromisoformat(down_time_str)
            up_time = time.fromisoformat(up_time_str) if up_time_str else None

            ticket = Ticket.objects.create(
                machine=machine,
                down_time=down_time,
                up_time=up_time,
                issue_list=issue,
                remarks=remarks,
                department=department
            )
            parts = Part.objects.filter(id__in=part_ids)
            ticket.parts.set(parts)
            ticket.save()

            return redirect('/')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, '(homepage)/ticket.html', {
        'machines': machines,
        'issues': issues,
        'departments': departments
    })