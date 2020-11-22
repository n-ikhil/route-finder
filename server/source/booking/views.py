from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from requests.api import request
from .models import Buses, OperatingCities, Booking
from .logic import *


def index(request):

    if not request.user.is_authenticated:
        return redirect(reverse("accounts:log_in"))

    if request.user.is_superuser:
        # all the core logic supposed to be here
        cityList = OperatingCities.objects.all()
        return render(request, "admin_city_list.html", {"cityList": cityList})
    else:
        if request.method == "GET":
            cityList = OperatingCities.objects.all()
            return render(request, "new_booking.html", {"cityList": cityList})
        else:
            # print(request.POST)
            start = request.POST.get("submit1")
            end = request.POST.get("submit2")
            [st_lat, st_long] = start.split("$")
            [end_lat, end_long] = end.split("$")
            # print(st_lat, st_long, end_lat, end_long)
            # location = geolocator.reverse((st_lat, st_long), exactly_one=True)
            # address = location.raw['address']
            # cur_city = address.get('city', '')
            cur_city = request.POST.get("city")
            if not OperatingCities.objects.filter(city=cur_city).exists():
                return redirect("/status/~")
            try:
                Booking.objects.get(user=request.user).delete()
            except:
                pass
            Booking.objects.update_or_create(
                user=request.user,
                src_lat=st_lat,
                src_long=st_long,
                dst_lat=end_lat,
                dst_long=end_long,
                city=cur_city,
                etime=request.POST.get("etime")
            )
            return redirect("/status/~")


def status(request, city=""):

    if not request.user.is_authenticated:
        return redirect("log_in")
    if request.user.is_superuser:
        city = "Delhi"
        # city = request.GET.get("")
        bookingList = Booking.objects.all().filter(city=city)
        city = OperatingCities.objects.get(city=city)
        busList = Buses.objects.all().filter(city=city)
        print(city, bookingList, busList)
        create_route(city, busList, bookingList)
        return render(request, "plain.html", {"data": city})
    else:
        if request.method == "GET":
            res = Booking.objects.filter(user=request.user.id).exists()
            if(not res):
                return render(request, "plain.html", {"data": "No booking in your name or City is not served"})

                # return HttpResponse("No booking in your name or City is not served")
            res = Booking.objects.filter(user=request.user.id)
            res = res[0]
            if(res.confirmed):
                return render(request, "plain.html", {"data": "your booking is confirmed"})
                # return HttpResponse("your booking is confirmed")
            else:
                return render(request, "plain.html", {"data": "your booking is under process"})
                # return HttpResponse("your booking is under process")
