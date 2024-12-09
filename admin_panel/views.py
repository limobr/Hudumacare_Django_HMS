from datetime import date
from django.utils import timezone
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from appointments.models import Appointment, Prescription
from doctor_panel.models import AppointmentType, Department
from landing.models import Contact
from accounts.models import DoctorContactInfo, DoctorExperience, DoctorLicensing, UserProfile, DoctorEducation, DoctorAvailability
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
# Create your views here.

def dashboard(request):
    # Get counts for doctors and patients
    doctor_count = UserProfile.objects.filter(usertype='doctor').count()
    patient_count = UserProfile.objects.filter(usertype='patient').count()

    # Get counts for different appointment statuses
    attended_count = Appointment.objects.filter(appointment_status='approved').count()
    pending_count = Appointment.objects.filter(appointment_status='pending').count()
    cancelled_count = Appointment.objects.filter(appointment_status='cancelled').count()

    # Get upcoming appointments sorted by closest date and time
    now = timezone.now()
    upcoming_appointments = Appointment.objects.filter(appointment_date__gte=now.date()) \
                                              .order_by('appointment_date', 'appointment_time')[:5]

    # Fetch doctors with their specialization
    doctors_with_specialization = UserProfile.objects.filter(usertype='doctor').prefetch_related(
        'user__doctoreducation_set')  # Prefetch the DoctorEducation for each doctor

    # Fetch new patients and their conditions
    new_patients = UserProfile.objects.filter(usertype='patient').prefetch_related(
        'user__patientmedicalinfo_set').order_by('-user__date_joined')[:5]

    # Pass the counts, appointments, doctors, and patients to the template
    return render(request, 'administration/admin_dashboard.html', {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'attended_count': attended_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
        'upcoming_appointments': upcoming_appointments,
        'doctors_with_specialization': doctors_with_specialization,
        'new_patients': new_patients,  # Add new patients data
    })


def doctors(request):
    # Get all users with 'doctor' usertype
    doctor_users = User.objects.filter(userprofile__usertype='doctor')

    # Get their education and availability
    doctors_data = []
    for doctor in doctor_users:
        # Get the latest education for the doctor
        education = DoctorEducation.objects.filter(user=doctor).order_by('-completion_date').first()
        specialization = education.specialization.name if education and education.specialization else "Not updated"
        
        # Check for availability status
        availability = DoctorAvailability.objects.filter(doctor=doctor).first()
        availability_status = availability.status if availability else "Unavailable"

        # Collect contact info
        contact_info = DoctorContactInfo.objects.filter(user=doctor).first()

        # Collect experience info
        experience = DoctorExperience.objects.filter(user=doctor).first()

        # Licensing info
        licensing = DoctorLicensing.objects.filter(user=doctor).first()

        # Append doctor data
        doctors_data.append({
            'doctor': doctor,
            'specialization': specialization,
            'availability_status': availability_status,
            'contact_info': contact_info,
            'experience': experience,
            'licensing': licensing,
            'profile_picture': doctor.userprofile.profile_picture
        })

    return render(request, "administration/doctors.html", {'doctors_data': doctors_data})


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

    return render(request, 'administration/patients.html', {'patients': patients})

def appointments(request):
    # Fetch all appointments
    appointments = Appointment.objects.select_related('patient').prefetch_related('patient__userprofile')
    
    # Calculate age for each patient in the appointments
    for appointment in appointments:
        appointment.patient.age = calculate_age(appointment.patient.userprofile.date_of_birth)  # Add 'age' to each patient

    return render(request, 'administration/appointments.html', {'appointments': appointments})

def doctors_schedules(request):
    return render(request, "administration/schedules.html")

def add_doctor(request):
    if request.method == 'POST':
        # Capture the form data and validate
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password'].strip()  # Strip spaces
        password_confirm = request.POST['confirm_password'].strip()  # Strip spaces
        gender = request.POST['gender']
        date_of_birth = request.POST['date_of_birth']

        # Debugging: Check values
        print(f"Password: {password}")
        print(f"Confirm Password: {password_confirm}")

        # 1. Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken. Please choose another one.")
            return render(request, 'administration/add_doctor.html', {'post_data': request.POST})  # Pass the form data back

        # 2. Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, 'administration/add_doctor.html', {'post_data': request.POST})  # Pass the form data back

        # 3. Check if passwords match
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'administration/add_doctor.html', {'post_data': request.POST})  # Pass the form data back

        try:
            # 4. Create the User object
            user = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=make_password(password),  # Hash the password before saving
            )

            # 5. Create the UserProfile object for the doctor
            UserProfile.objects.create(
                user=user,
                usertype='doctor',
                gender=gender,
                date_of_birth=date_of_birth
            )

            messages.success(request, "Doctor account created successfully.")
            return redirect('admin_doctors')  # Redirect to the doctor list page after success

        except IntegrityError:
            messages.error(request, "An error occurred while creating the account.")
            return render(request, 'administration/add_doctor.html', {'post_data': request.POST})  # Pass the form data back

    else:
        # For GET request, render the empty form
        return render(request, 'administration/add_doctor.html')  # Ensure the form is rendered for GET requests


def retrieve_contacts(request):
    contacts = Contact.objects.all().order_by('-created_at')  # Retrieve all contacts and order by most recent
    return render(request, "administration/retrieve_contacts.html", {'contacts': contacts})

def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)  # Retrieve the contact or show 404 if not found
    contact.delete()  # Delete the contact
    return redirect('admin_contacts')  # Redirect back to the contacts page



def departments(request):
    departments = Department.objects.all()  
    return render(request, 'administration/departments.html', {'departments': departments})

def create_doctor(request):
    return render(request, "administration/departments.html")

def add_department(request):
    if request.method == 'POST':
        department_name = request.POST.get('name')
        description = request.POST.get('description')

        
        department = Department(name=department_name, description=description)
        department.save()

  
        return redirect('admin_departments')
    
    return render(request, 'administration/add_department.html')

def appointment_types(request):
    appointment_types = AppointmentType.objects.all()

    return render(request, 'administration/appointmenttypes.html', {'appointment_types': appointment_types})

def add_appointmenttype(request):
    if request.method == 'POST':
        appointment_name = request.POST.get('name')
        description = request.POST.get('description')

        appointment_type = AppointmentType(name=appointment_name, description=description)
        appointment_type.save()

        return redirect('admin_appointmentstypes')
    
    return render(request, 'administration/add_appointmenttype.html')

def prescription_list(request):
    prescriptions = Prescription.objects.all()

    # Prepare the data to be passed into the template
    prescriptions_data = []
    for prescription in prescriptions:
        appointment = prescription.appointment
        # Fetching patient and doctor names from the UserProfile model
        doctor = User.objects.get(id=appointment.doctor.id)  # Assuming 'doctor' field on appointment points to the doctor
        patient = User.objects.get(id=appointment.patient.id)  # Assuming 'patient' field on appointment points to the patient

        prescriptions_data.append({
            'prescription': prescription,
            'doctor_name': f"{doctor.first_name} {doctor.last_name}",
            'patient_name': f"{patient.first_name} {patient.last_name}",
        })
    
    return render(request, 'administration/prescriptions.html', {'prescriptions': prescriptions_data})