from django.urls import path
from doctor_panel import views

urlpatterns = [
    path("", views.dashboard, name="doctor_dashboard"),
    path("patients/", views.patients, name="doctor_patients"),
    path('appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('appointments/confirm/<int:appointment_id>/', views.confirm_appointment, name='doctor_confirm_appointment'),
    path("schedules/", views.my_schedules, name="doctor_schedules"),
    path("add-patient/", views.add_patient, name="doctor_add_patient"),
    path("patient-history/", views.patient_history, name="doctor_history"),
    path("departments/", views.departments, name="doctor_departments"),
    path("records/", views.medical_records, name="doctor_records"),
    path("prescriptions/", views.prescriptions, name="doctor_prescriptions"),
    path('my-publications/', views.my_publications, name='my_publications'),
    path('edit-resource/<int:id>/', views.edit_resource, name='edit_resource'),
    path('appointments/<int:appointment_id>/prescribe/', views.add_prescription, name='doctor_add_prescription'),
]