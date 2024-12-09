from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from doctor_panel.models import Department

# Create your models here.
# both 
class UserProfile(models.Model):
    USER_TYPES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('admin', 'Admin'),  # Added admin usertype
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usertype = models.CharField(max_length=10, choices=USER_TYPES)
    gender = models.CharField(max_length=10)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.usertype}"

    
############################################## Doctor ###################################################

# Doctor_ContactInfo
class DoctorContactInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    emergency_number = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

# Doctor_Education
class DoctorEducation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=255)
    award = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    specialization = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} - {self.award}"

# Doctor_Experience
class DoctorExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    job_position = models.CharField(max_length=100)
    period_from = models.DateField(null=True, blank=True)
    period_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.job_position}"

# Doctor_Licensing
class DoctorLicensing(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50)
    license_issuing_authority = models.CharField(max_length=100, null=True, blank=True)
    license_expiry = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.license_number}"

# Doctor_Availability
class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    
    # Boolean fields for each day of the week
    monday_available = models.BooleanField(default=False)
    tuesday_available = models.BooleanField(default=False)
    wednesday_available = models.BooleanField(default=False)
    thursday_available = models.BooleanField(default=False)
    friday_available = models.BooleanField(default=False)
    saturday_available = models.BooleanField(default=False)
    sunday_available = models.BooleanField(default=False)
    
    # Time fields for start and end times for each day
    monday_start_time = models.TimeField(null=True, blank=True)
    monday_end_time = models.TimeField(null=True, blank=True)
    
    tuesday_start_time = models.TimeField(null=True, blank=True)
    tuesday_end_time = models.TimeField(null=True, blank=True)
    
    wednesday_start_time = models.TimeField(null=True, blank=True)
    wednesday_end_time = models.TimeField(null=True, blank=True)
    
    thursday_start_time = models.TimeField(null=True, blank=True)
    thursday_end_time = models.TimeField(null=True, blank=True)
    
    friday_start_time = models.TimeField(null=True, blank=True)
    friday_end_time = models.TimeField(null=True, blank=True)
    
    saturday_start_time = models.TimeField(null=True, blank=True)
    saturday_end_time = models.TimeField(null=True, blank=True)
    
    sunday_start_time = models.TimeField(null=True, blank=True)
    sunday_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.doctor.username} Availability'

    class Meta:
        verbose_name_plural = 'Doctor Availability'

    
################################################### Patients models #################################

# Patient_UserProfile

# Patient_ContactInfo
class PatientContactInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

# Patient_MedicalInfo
class PatientMedicalInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    primary_diagnosis = models.CharField(max_length=255, null=True, blank=True)
    secondary_diagnosis = models.CharField(max_length=255, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    blood_type = models.CharField(max_length=3, null=True, blank=True)
    chronic_conditions = models.TextField(null=True, blank=True)
    past_surgery = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# Patient_InsuranceInfo
class PatientInsuranceInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    insurance_provider = models.CharField(max_length=100, null=True, blank=True)
    policy_number = models.CharField(max_length=100, null=True, blank=True)
    coverage_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.insurance_provider}"

# Patient_SocialInfo
class PatientSocialInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    children = models.IntegerField(default=0, null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username


#####################################notification #############################################

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user receiving the notification
    notification_text = models.TextField()  # Notification content (e.g., "You have a new appointment")
    link = models.URLField(null=True, blank=True)  # Optional link to view the related resource (like appointment)
    created_at = models.DateTimeField(default=now)  # When the notification was created
    is_read = models.BooleanField(default=False)  # To track read/unread status

    def __str__(self):
        return f"Notification for {self.user.username} - {self.notification_text[:50]}"