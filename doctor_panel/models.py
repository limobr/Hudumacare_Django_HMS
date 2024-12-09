from django.db import models

# Create your models here.
class Department(models.Model):
    # Department name (e.g., Dentistry, Neurology, Orthopedics)
    name = models.CharField(max_length=100, unique=True)
    
    # Description of the department
    description = models.TextField()
    
    # Time when the department was created
    time_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Departments'
        
class AppointmentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'AppointmentTypes'