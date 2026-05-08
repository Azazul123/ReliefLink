# Status/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.status, name="status"),

    path('district/<int:division_id>/', views.district_status, name="district_status"),
    path('upazila/<int:district_id>/', views.upazila_status, name="upazila_status"),
    path('union/<int:upazila_id>/', views.union_status, name="union_status"),
    path('ward/<int:union_id>/', views.ward_status, name="ward_status"),
    path('house/<int:ward_id>/', views.house_status, name="house_status"),
]