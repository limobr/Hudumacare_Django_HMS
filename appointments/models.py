from django.db import models
from django.contrib.auth.models import User
from doctor_panel.models import AppointmentType, Department

class Appointment(models.Model):
    patient = models.ForeignKey(User, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, related_name='doctor_appointments', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)  # Added department field
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    )
    appointment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        doctor_username = self.doctor.username if self.doctor else "No Doctor Assigned"
        return f"Appointment: {self.patient.username} with {doctor_username} in {self.department.name if self.department else 'No Department'} on {self.appointment_date}"

    class Meta:
        verbose_name_plural = 'Appointments'


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')  # Links to Appointment
    doctor_remarks = models.TextField(null=True, blank=True)  # Doctor's remarks
    prescribed_drugs = models.TextField()  # List of prescribed drugs and their details
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount for the drugs
    prescription_date = models.DateTimeField(auto_now_add=True)  # Automatically adds the current date and time
    payed = models.BooleanField(default=False)  # Boolean field to track whether the prescription is paid or not

    def __str__(self):
        return f"Prescription for Appointment ID: {self.appointment.id}"

    class Meta:
        verbose_name_plural = 'Prescriptions'
