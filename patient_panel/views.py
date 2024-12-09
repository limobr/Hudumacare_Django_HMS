from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# import json
# import requests
from django.http import HttpResponse
from accounts.models import DoctorAvailability, DoctorContactInfo, DoctorEducation, DoctorExperience, DoctorLicensing, Notification, UserProfile
from appointments.models import Appointment, Prescription
from doctor_panel.models import AppointmentType, Department
from django.contrib import messages
# from .credentials import LipanaMpesaPpassword, MpesaAccessToken
# from requests.auth import HTTPBasicAuth

# Create your views here.

def dashboard(request):
    return render(request, "patient/patient_dashboard.html")

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(notification.link)

@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    next_url = request.GET.get('next', '/')
    return redirect(next_url)

def notifications_processor(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Fetch unread notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user).order_by('-date')
        unread_count = notifications.filter(status='unread').count()
        return {
            'notifications': notifications,
            'unread_count': unread_count
        }
    return {}

def create_appointment_notifications(appointment):
    # Notification for the patient
    Notification.objects.create(
        user=appointment.patient,
        notification_text=f"Your appointment with Dr. {appointment.doctor.username} has been successfully created.",
        link=f"/appointments/{appointment.id}/"
    )
    
    # Notification for the doctor
    Notification.objects.create(
        user=appointment.doctor,
        notification_text=f"You have a new appointment with {appointment.patient.username}.",
        link=f"/appointments/{appointment.id}/"
    )


@login_required
def book_appointment(request):
    # Get available departments and appointment types
    departments = Department.objects.all()
    appointment_types = AppointmentType.objects.all()

    if request.method == "POST":
        # Get form data from POST request
        department_id = request.POST.get('department')
        appointment_type_id = request.POST.get('appointment_type')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        # Get the patient (current logged in user)
        patient = request.user

        # Check for valid department and appointment type
        try:
            department = Department.objects.get(id=department_id)
            appointment_type = AppointmentType.objects.get(id=appointment_type_id)

            # Create the appointment instance (with no doctor initially)
            appointment = Appointment.objects.create(
                patient=patient,
                department=department,
                appointment_type=appointment_type,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                reason=reason,
            )

            # Check if the doctor is missing (no doctor assigned yet)
            if not appointment.doctor:
                return redirect('choose_doctor', appointment_id=appointment.id)  # Redirect to choose doctor page

            # Redirect to patient appointments list
            return redirect('patient_appointments')  # Replace with your actual success URL
        except Department.DoesNotExist or AppointmentType.DoesNotExist:
            return render(request, 'patient/book_appointment.html', {
                'departments': departments,
                'appointment_types': appointment_types,
                'error_message': 'Invalid department or appointment type selected.',
            })
    
    return render(request, 'patient/book_appointment.html', {
        'departments': departments,
        'appointment_types': appointment_types
    })

@login_required
def choose_doctor(request, appointment_id):
    # Get the appointment to display its details
    appointment = Appointment.objects.get(id=appointment_id)

    # Filter doctors who specialize in the selected department
    doctors = UserProfile.objects.filter(usertype='doctor')
    specialized_doctors = []
    for doctor in doctors:
        # Check if the doctor has specialization in the same department
        try:
            doctor_education = DoctorEducation.objects.get(user=doctor.user, specialization=appointment.department)
            specialized_doctors.append(doctor)
        except DoctorEducation.DoesNotExist:
            continue

    if request.method == "POST":
        # Get the selected doctor from the POST request
        doctor_id = request.POST.get('doctor')
        try:
            selected_doctor = User.objects.get(id=doctor_id)
            # Update the appointment with the selected doctor
            appointment.doctor = selected_doctor
            appointment.save()

            # Call the function to create notifications for both the doctor and the patient
            create_appointment_notifications(appointment)

            return redirect('patient_appointments')  # Redirect to the appointments list page
        except User.DoesNotExist:
            # Handle invalid doctor selection
            return render(request, 'patient/choose_doctor.html', {
                'appointment': appointment,
                'doctors': specialized_doctors,
                'error_message': 'Invalid doctor selected.',
            })

    return render(request, 'patient/choose_doctor.html', {
        'appointment': appointment,
        'doctors': specialized_doctors,
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

    return render(request, "patient/doctors.html", {'doctors_data': doctors_data})


@login_required
def my_appointments(request):
    # Get the patient's appointments
    appointments = Appointment.objects.filter(patient=request.user)

    # Check if there's any appointment without a doctor
    missing_doctor_appointment = appointments.filter(doctor__isnull=True).first()

    if missing_doctor_appointment:
        # Create a message for the user
        messages.info(request, f"Hello {request.user.first_name}, please choose a doctor for the appointment you made on {missing_doctor_appointment.appointment_date}.")

        # Redirect to choose a doctor if there is an appointment without a doctor
        return redirect('choose_doctor', appointment_id=missing_doctor_appointment.id)

    return render(request, 'patient/my_appointments.html', {'appointments': appointments})

def my_medical_records(request):
    return render(request, "patient/my_records.html")

@login_required
def my_prescriptions(request):
    # Get the logged-in patient's profile
    user_profile = UserProfile.objects.get(user=request.user)

    # Fetch the prescriptions for the logged-in patient
    if user_profile.usertype == 'patient':
        prescriptions = Prescription.objects.filter(appointment__patient=request.user)
    else:
        prescriptions = []

    # Prepare the data to pass to the template
    prescriptions_data = []
    for prescription in prescriptions:
        appointment = prescription.appointment
        doctor = User.objects.get(id=appointment.doctor.id)  # Fetch doctor
        patient = User.objects.get(id=appointment.patient.id)  # Fetch patient

        prescriptions_data.append({
            'prescription': prescription,
            'doctor_name': f"{doctor.first_name} {doctor.last_name}",
            'patient_name': f"{patient.first_name} {patient.last_name}",
        })
    
    return render(request, "patient/my_prescriptions.html", {'prescriptions': prescriptions_data})

def health_education(request):
    return render(request, "patient/health_education.html")

def settings(request):
    return render(request, "patient/settings.html")

def help(request):
    return render(request, "patient/help.html")

@login_required
def edit_appointment(request, appointment_id):
    # Fetch the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if request.method == 'POST':
        # Get data from the form
        department_id = request.POST.get('department')
        appointment_type_id = request.POST.get('appointment_type')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        try:
            department = Department.objects.get(id=department_id)
            appointment_type = AppointmentType.objects.get(id=appointment_type_id)

            # Check if the department has changed
            if department != appointment.department:
                # Clear the doctor field if department has changed
                appointment.doctor = None
                appointment.department = department  # Update department

            # Update other fields
            appointment.appointment_type = appointment_type
            appointment.appointment_date = appointment_date
            appointment.appointment_time = appointment_time
            appointment.reason = reason

            # Save the appointment after making changes
            appointment.save()

            # If department was changed, redirect to choose doctor page
            if department != appointment.department:
                return redirect('choose_doctor', appointment_id=appointment.id)

            # Redirect back to the patient appointments page after saving the appointment
            return redirect('patient_appointments')

        except Department.DoesNotExist or AppointmentType.DoesNotExist:
            error_message = "Invalid department or appointment type selected."
            return render(request, 'patient/patient_edit_appointment.html', {
                'appointment': appointment,
                'error_message': error_message
            })

    # If GET request, pre-populate form with existing appointment data
    departments = Department.objects.all()
    appointment_types = AppointmentType.objects.all()
    return render(request, 'patient/patient_edit_appointment.html', {
        'appointment': appointment,
        'departments': departments,
        'appointment_types': appointment_types
    })


    
@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)

    if request.method == 'POST':
        appointment.delete()
        return redirect('patient_appointments')  # Redirect back to the appointments page

    # If GET request, render confirmation modal
    return redirect('patient_appointments')

# # Generate the ID of the transaction
# def token(request):
#     """ Generates the ID of the transaction """
#     consumer_key = 'u4FB9kwVnP9Bw53kg5fKeDbRnzNwb9TLvBzmbVAZUgF55Vgg'
#     consumer_secret = 'j7UC9AECTyZ725lNCPvaM40WxtBDYCIOhSGdtlTYOoOJlbK3MLxwwVJ3AoDtNLxf'
#     api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

#     r = requests.get(api_URL, auth=HTTPBasicAuth(
#         consumer_key, consumer_secret))
#     mpesa_access_token = json.loads(r.text)
#     validated_mpesa_access_token = mpesa_access_token["access_token"]

#     return render(request, 'token.html', {"token":validated_mpesa_access_token})


# # Send the stk push
# def stk(request):
#     """ Sends the stk push prompt """
#     if request.method =="POST":
#         phone = request.POST['phone']
#         amount = request.POST['amount']
#         access_token = MpesaAccessToken.validated_mpesa_access_token
#         api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#         headers = {"Authorization": "Bearer %s" % access_token}
#         request = {
#             "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
#             "Password": LipanaMpesaPpassword.decode_password,
#             "Timestamp": LipanaMpesaPpassword.lipa_time,
#             "TransactionType": "CustomerPayBillOnline",
#             "Amount": amount,
#             "PartyA": phone,
#             "PartyB": LipanaMpesaPpassword.Business_short_code,
#             "PhoneNumber": phone,
#             "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
#             "AccountReference": "eMobilis",
#             "TransactionDesc": "Web Development Charges"
#         }
#         response = requests.post(api_url, json=request, headers=headers)
#         return HttpResponse("Success")