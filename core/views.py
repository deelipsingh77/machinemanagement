from calendar import c
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, Location

@login_required(login_url="login")
def add_location(request):
    if request.method == "POST":
        location_name = request.POST.get("location")
        if location_name:
            Location.objects.create(location=location_name)
            messages.success(request, "Location added successfully.")
            return redirect(
                "add_location"
            )  # Redirect to the same page or another as needed
        else:
            messages.error(request, "Location name cannot be empty.")

    locations = (
        Location.objects.all()
    )  # Fetch all locations for displaying in the table

    context = {"locations": locations}
    return render(request, "(core)/add_location.html", context)

@login_required(login_url="login")
def add_department(request):
    if request.method == "POST":
        department_name = request.POST.get("department")
        if department_name:
            Department.objects.create(name=department_name)
            messages.success(request, "Department added successfully.")
            return redirect(
                "add_department"
            )  # Redirect to the same page or another as needed
        else:
            messages.error(request, "Department name cannot be empty.")
            
    departments = (
        Department.objects.all()
    )  # Fetch all departments for displaying in the table
    
    context = {"departments": departments}
    return render(request, "(core)/add_department.html", context)

@login_required(login_url="login")
def remove_department(request, id):
    department = Department.objects.get(id=id)
    department.delete()
    messages.success(request, "Department removed successfully.")
    return redirect("add_department")

@login_required(login_url="login")
def remove_location(request, id):
    location = Location.objects.get(id=id)
    location.delete()
    messages.success(request, "Location removed successfully.")
    return redirect("add_location")
