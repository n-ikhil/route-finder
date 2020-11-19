from os import name
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='normal_booking'),
    path('admin_booking', views.adminView, name="admin_booking")
]
