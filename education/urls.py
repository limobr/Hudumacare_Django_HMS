from django.urls import path
from . import views

urlpatterns = [
    path('add-category/', views.add_category, name='add_category'),
    
    # Resource URLs
    path('add-resource/', views.add_resource, name='add_resource'),
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/<slug:slug>/', views.resource_detail, name='resource_detail'),

    # (Optional) Add a search functionality URL
    path('search/', views.resource_list, name='resource_search'),
    path('go-home/', views.home_redirect, name='home_redirect'),
]