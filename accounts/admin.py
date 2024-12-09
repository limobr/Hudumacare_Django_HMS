from django.contrib import admin
from accounts.models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(DoctorContactInfo)
admin.site.register(DoctorEducation)
admin.site.register(DoctorExperience)
admin.site.register(DoctorLicensing)
admin.site.register(DoctorAvailability)
admin.site.register(PatientMedicalInfo)
admin.site.register(PatientContactInfo)
admin.site.register(PatientSocialInfo)
admin.site.register(PatientInsuranceInfo)
admin.site.register(Notification)