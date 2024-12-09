from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.view_patient_profile, name='patient_profile'),
    path('doctor-profile/', views.doctor_profile, name='doctor_profile'),
    path('edit-doctor-profile/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('edit-patient-profile/', views.edit_patient_profile, name='edit_patient_profile'),
    path('delete-experience/', views.delete_experience, name='patient_delete_experience'),
]