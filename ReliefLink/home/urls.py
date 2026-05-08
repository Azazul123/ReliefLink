# home/urls.py

from django.urls import path, include
from . import views
from django.contrib.auth.urls import views as auth_views

urlpatterns = [
    path('', views.index, name='home'),
    path('service/', views.service, name='service'),
    path('contact/', views.contact, name='contact'),
    
    path('dashboard/', views.dashboard, name='dashboard'),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('divisionalcommissioner_dashboard/', views.divisionalcommissioner_dashboard, name='divisionalcommissioner_dashboard'),

    path('deputycommissioner_dashboard/', views.deputycommissioner_dashboard, name='deputycommissioner_dashboard'),

    path('uno_dashboard/', views.uno_dashboard, name='uno_dashboard'),

    path('unionchairman_dashboard/', views.unionchairman_dashboard, name='unionchairman_dashboard'),

    path('wardmember_dashboard/', views.wardmember_dashboard, name='wardmember_dashboard'),

    path('public_dashboard/', views.public_dashboard, name='public_dashboard'),

    path('update_flood_status/', views.update_flood_status, name = 'update_flood_status'),

    path('relief_supply/<int:house_id>/', views.relief_supply, name='relief_supply'),


]