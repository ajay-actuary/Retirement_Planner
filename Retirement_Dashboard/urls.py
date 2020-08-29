from django.urls import path, re_path
from django.contrib import admin
from . import views

app_name = 'Retirement_Dashboard'
urlpatterns = [
    # ex: /polls/
    re_path('Dashboard', views.DashboardView, name='Dashboard'),
    re_path('DashOutput', views.DashboardOutputView, name='DashOutput'),
]