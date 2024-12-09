from django.urls import path
from admin_panel import views

urlpatterns = [
    path("", views.dashboard, name="admin_dashboard"),
    path("doctors", views.doctors, name="admin_doctors"),
    path("patients", views.patients, name="admin_patients"),
    path("appointments", views.appointments, name="admin_appointments"),
    path("add-department", views.add_department, name="add_department"),
    path("schedules", views.doctors_schedules, name="admin_schedules"),
    path("departments", views.departments, name="admin_departments"),
    path("appointment-types", views.appointment_types, name="admin_appointmentstypes"),
    path("add-appointment-types", views.add_appointmenttype, name="add_appointment_type"),
    path("add-doctor", views.add_doctor, name="add_doctor"),
    path("retrieve-contacts", views.retrieve_contacts, name="admin_contacts"),
    path('contacts/delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('prescriptions/', views.prescription_list, name='admin_prescription_list'),
]