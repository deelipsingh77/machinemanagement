from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def reports(request):
    pass