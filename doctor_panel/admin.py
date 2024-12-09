from django.contrib import admin

from doctor_panel.models import Department, AppointmentType

# Register your models here.


admin.site.register(Department)
admin.site.register(AppointmentType)