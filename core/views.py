from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home(_):
    return redirect('dashboard')

@login_required(login_url='login')
def dashboard(request):
    return render(request, '(core)/dashboard.html')
