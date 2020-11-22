from os import name
from .views import *
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='booking'),
    path('status/<str:city>', views.status, name="status")
    # path('admin_booking', views.adminView, name="admin_booking")
]
