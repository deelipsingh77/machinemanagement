from django.shortcuts import render

# Create your views here.
def homepage(request):
    return render(request, '(homepage)/home.html')

def ticket(request):
    return render(request, '(homepage)/ticket.html')