from calendar import c
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Location

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
