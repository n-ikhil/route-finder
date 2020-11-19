from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Buses, OperatingCities, Booking


def index(request):
    if(request.user.is_superuser):
        return redirect(reverse("admin_booking"))
    if(not request.user.is_authenticated):
        return redirect(reverse("accounts:log_in"))
    return render(request, "new_booking.html")
    # return HttpResponse("Hello, world. You're at the booking index.")


def adminView(request):
    if((not request.user.is_superuser) or (not request.user.is_authenticated)):
        return redirect(reverse("normal_booking"))
    # all the core logic supposed to be here
    if(not OperatingCities.objects.get(city=request.city)):
        return HttpResponse("not servicable here")
    busList = Buses.objects.filter(city=request.city, working=True)
    bookingList = Booking.objects.filter(city=request.city)
    if((not busList) or (not bookingList)):
        return HttpResponse("no buses or customers available here")

    return HttpResponse("Hello, world. You're at the admin booking index.")
