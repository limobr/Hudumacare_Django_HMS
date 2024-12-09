from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='landing_home'),
    path('about/', views.about, name='landing_about'),
    path('gallery/', views.gallery, name='landing_gallery'),
    path('contact/', views.contact, name='landing_contact'),
    path('services/', views.services, name='landing_services'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
]