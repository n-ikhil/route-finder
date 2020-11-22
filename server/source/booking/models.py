from django.db import models
from django.contrib.auth.models import User


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    src_lat = models.CharField(max_length=100)
    src_long = models.CharField(max_length=100)
    dst_lat = models.CharField(max_length=100)
    dst_long = models.CharField(max_length=100)
    # stime = models.CharField(max_length=100)
    etime = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    # distance between start and end, based on the path
    # distance = models.IntegerField()
    # meaning this booking is  confirmed
    osxsid = models.IntegerField(default=1)
    osxdid = models.IntegerField(default=1)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class OperatingCities(models.Model):
    city = models.CharField(max_length=100)

    def __str__(self):
        return str(self.city)


class Buses(models.Model):
    city = models.ForeignKey(OperatingCities, on_delete=models.CASCADE)
    fuelefficiency = models.IntegerField()# rupee per unit dist
    working = models.BooleanField(default=True)

    # whether the bus is usable
