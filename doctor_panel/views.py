from datetime import date
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import DoctorAvailability, Notification, PatientContactInfo, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

from appointments.models import Appointment, Prescription
from education.forms import PatientEducationResourceForm
from education.models import PatientEducationResource
from django.utils.timezone import localtime
from django.contrib import messages

# Create your views here.

def dashboard(request):
    return render(request, "doctor/doctor_dashboard.html")

def doctors(request):
    return render(request, "doctor/doctors.html")

def calculate_age(birth_date):
    today = date.today()
    if birth_date:
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return None 

def patients(request):
    # Fetch all patients with their contact info using prefetch_related
    patients = UserProfile.objects.filter(usertype='patient').prefetch_related('user__patientcontactinfo')
    
    # Calculate age for each patient
    for patient in patients:
        patient.age = calculate_age(patient.date_of_birth)  # Add an 'age' attribute to each patient

    return render(request, 'doctor/patients.html', {'patients': patients})


def my_schedules(request):
    return render(request, "doctor/schedules.html")

def add_patient(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        date_of_birth = request.POST['date_of_birth']
        gender = request.POST['gender']
        address = request.POST['address']
        phone = request.POST['phone']

        # Validate password confirmation
        if password != confirm_password:
            return render(request, "doctor/add_patient.html", {'error': "Passwords do not match"})

        # Create user
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=make_password(password)  # Hashing the password
        )

        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            usertype='patient',  # Automatically set to 'patient'
            gender=gender,
            date_of_birth=date_of_birth
        )

        # Create PatientContactInfo
        PatientContactInfo.objects.create(
            user=user,
            address=address,
            phone=phone
        )

        # Redirect to patients list after successful creation
        return redirect('doctor_patients')

    return render(request, "doctor/add_patient.html")

def patient_history(request):
    return render(request, "doctor/history.html")

def departments(request):
    return render(request, "doctor/departments.html")

def medical_records(request):
    return render(request, "doctor/records.html")

def prescriptions(request):
    # Get the logged-in doctor's user profile
    doctor_profile = UserProfile.objects.get(user=request.user, usertype='doctor')

    # Get all prescriptions related to this doctor
    prescriptions = Prescription.objects.filter(appointment__doctor=doctor_profile.user)

    # Prepare the data to be passed into the template
    prescriptions_data = []
    for prescription in prescriptions:
        appointment = prescription.appointment
        patient = User.objects.get(id=appointment.patient.id)  # Assuming 'patient' field on appointment points to the patient

        prescriptions_data.append({
            'prescription': prescription,
            'doctor_name': f"{doctor_profile.user.first_name} {doctor_profile.user.last_name}",  # Doctor's name
            'patient_name': f"{patient.first_name} {patient.last_name}",  # Patient's name
        })

    return render(request, 'doctor/prescriptions.html', {'prescriptions': prescriptions_data})

def my_publications(request):
    """View to list resources authored by the logged-in user."""
    resources = PatientEducationResource.objects.filter(author=request.user)
    context = {
        'resources': resources
    }
    return render(request, 'doctor/my_publications.html', context)

def edit_resource(request, id):
    resource = get_object_or_404(PatientEducationResource, id=id)

    if request.method == 'POST':
        form = PatientEducationResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            return redirect('my_publications')  # Redirect to your list of publications
    else:
        form = PatientEducationResourceForm(instance=resource)

    return render(request, 'doctor/edit_resource.html', {'form': form, 'resource': resource})

@login_required
def doctor_appointments(request):
    # Get the logged-in doctor's profile
    doctor_profile = get_object_or_404(UserProfile, user=request.user, usertype='doctor')
    
    # Fetch appointments for the logged-in doctor
    appointments = Appointment.objects.filter(doctor=doctor_profile.user).select_related('patient', 'department')
    
    # Calculate age for each patient and attach it to the appointments
    for appointment in appointments:
        appointment.patient.age = calculate_age(appointment.patient.userprofile.date_of_birth)  # Assuming date_of_birth is in userprofile

    return render(request, 'doctor/doctor_appointments.html', {'appointments': appointments})

@login_required
def confirm_appointment(request, appointment_id):
    # Fetch the appointment and ensure it belongs to the doctor
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    # Update the status to 'confirmed'
    appointment.appointment_status = 'confirmed'
    appointment.save()

    # Create the notification for the patient
    create_appointment_confirmation_notification(appointment)

    # Add a success message and redirect
    messages.success(request, 'Appointment confirmed successfully!')
    return redirect('doctor_appointments')

def create_appointment_confirmation_notification(appointment):
    # Create a notification text
    appointment_datetime = f"{appointment.appointment_date} {appointment.appointment_time}"
    notification_text = f"Your appointment with Dr. {appointment.doctor.username} on {appointment_datetime} has been confirmed."

    # Create and save the notification
    Notification.objects.create(
        user=appointment.patient,  # The patient receiving the notification
        notification_text=notification_text,
        link=f"/patient/appointments/",  # Optional link to the appointment details
        created_at=localtime(),  # Set to now
        is_read=False  # Mark as unread initially
    )

@login_required
def add_prescription(request, appointment_id):
    # Fetch the appointment and ensure it belongs to the doctor
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)

    if request.method == 'POST':
        # Get the form data
        doctor_remarks = request.POST.get('doctor_remarks')
        prescribed_drugs = request.POST.get('prescribed_drugs')
        amount = request.POST.get('amount')

        # Ensure that the form data is valid
        if doctor_remarks and prescribed_drugs and amount:
            # Create a new prescription and save it to the database
            prescription = Prescription.objects.create(
                appointment=appointment,
                doctor_remarks=doctor_remarks,
                prescribed_drugs=prescribed_drugs,
                amount=amount,
                prescription_date=timezone.now(),  # Assuming prescription_date is automatically set
            )

            # Save the prescription
            prescription.save()

            # Redirect to the doctor's appointments page after saving the prescription
            return redirect('doctor_appointments')
        else:
            # If any field is missing, return an error or reload the form with an error message
            return HttpResponseForbidden("Invalid form data. Please fill out all the fields.")
    
    # If not a POST request, return a forbidden error (this view should only handle POST requests)
    return HttpResponseForbidden("Invalid request method.")
