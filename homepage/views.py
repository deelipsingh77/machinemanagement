from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from core.models import MachinePart, Ticket, Machine, Part, Issue, Department

# Create your views here.
def homepage(request):
    return render(request, '(homepage)/home.html')


def ticket(request):
    machines = Machine.objects.all()
    issues = Issue.objects.all()
    departments = Department.objects.all()
    
    if request.method == 'POST':
        ticket_no = request.POST['ticket_no']
        machine_id = request.POST['machine']
        part_ids = request.POST.getlist('parts')
        down_time = request.POST['down_time']
        up_time = request.POST['up_time']
        issue_id = request.POST['issue_list']
        remarks = request.POST.get('remarks', '')
        department_id = request.POST['department']

        try:
            machine = get_object_or_404(Machine, id=machine_id)
            issue = get_object_or_404(Issue, id=issue_id)
            department = get_object_or_404(Department, id=department_id)
            
            ticket = Ticket.objects.create(
                ticket_no=ticket_no,
                machine=machine,
                down_time=down_time,
                up_time=up_time,
                issue_list=issue,
                remarks=remarks,
                department=department
            )
            ticket.parts.set(Part.objects.filter(id__in=part_ids))
            ticket.save()

            return redirect('/')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, '(homepage)/ticket.html', {
        'machines': machines,
        'issues': issues,
        'departments': departments
    })
