from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='patient_dashboard'),
    path('doctors/', views.doctors, name='patient_doctors'),
    path('appointments/', views.my_appointments, name='patient_appointments'),
    path('book_appointment/', views.book_appointment, name='book_appointment'),
    path('choose_doctor/<int:appointment_id>/', views.choose_doctor, name='choose_doctor'),
    path('medical-records/', views.my_medical_records, name='patient_records'),
    path('prescriptions/', views.my_prescriptions, name='patient_prescriptions'),
    path('education/', views.health_education, name='patient_education'),
    path('settings/', views.settings, name='patient_settings'),
    path('help/', views.help, name='patient_help'),
    path('appointments/edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    # path('stk/', views.stk, name='stk'),
    # path('token/', views.token, name='token'),
    path('notifications/mark/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/mark-all/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
]