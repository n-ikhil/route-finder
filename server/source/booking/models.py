from django.db import models
from django.contrib.auth.models import User


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    src = models.CharField(max_length=100)
    dst = models.CharField(max_length=100)
    stime = models.CharField(max_length=100)
    etime = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    # distance between start and end, based on the path
    distance = models.IntegerField()
    # meaning this booking is  confirmed
    confirmed = models.BooleanField(default=False)


class OperatingCities(models.Model):
    city = models.CharField(max_length=100)


class Buses(models.Model):
    city = models.ForeignKey(OperatingCities, on_delete=models.CASCADE)
    fuelefficiency = models.IntegerField()
    working = models.BooleanField(default=True)
    # whether the bus is usable
