from datetime import datetime
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from accounts.models import DoctorContactInfo, DoctorEducation, DoctorExperience, DoctorLicensing, PatientContactInfo, PatientInsuranceInfo, PatientMedicalInfo, PatientSocialInfo, UserProfile
from doctor_panel.models import Department

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on usertype
            user_profile = user.userprofile  # Assuming you have a userprofile model linked to the User
            if user_profile.usertype == 'doctor':
                return redirect('doctor_dashboard')  # Redirect to doctor dashboard
            elif user_profile.usertype == 'patient':
                return redirect('patient_dashboard')  # Redirect to patient dashboard
            elif user_profile.usertype == 'admin':
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            else:
                return redirect('home')  # Redirect to home if no specific usertype
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')

def user_logout(request):
    # Log out the user
    logout(request)
    # Redirect to the homepage or login page
    return redirect('landing_home')

def register(request):
    """Show the registration form and handle user registration"""
    if request.method == 'POST':
        # Get form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Start by checking if the passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        # Now check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        # Then check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use')
            return redirect('register')

        # If no error messages were added, proceed to create the user
        if not messages.get_messages(request):  # Check if there are no error messages
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()

            # Automatically create the UserProfile for the patient
            UserProfile.objects.create(
                user=user,
                usertype='patient',  # Assign 'patient' usertype automatically
                gender='',  # Optional: add these fields later via profile update
                date_of_birth=None  # Optional: handle this later via profile update
            )

            messages.success(request, "Account created successfully")
            return redirect('login')  # Redirect to login or homepage after successful registration

    return render(request, 'accounts/register.html')


def parse_date(date_string):
    if not date_string:  # If the date string is empty or None
        return None  # Or set a default value like datetime.now() or skip if that's acceptable
    
    for fmt in ('%d-%m-%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date format for {date_string} is not supported.")

@login_required
def doctor_profile(request):
    user = request.user  # Get the currently logged-in user

    try:
        # Fetch the associated profile, contact info, and other details
        user_profile = UserProfile.objects.get(user=user)
        doctor_contact = DoctorContactInfo.objects.get(user=user)
        doctor_education = DoctorEducation.objects.filter(user=user)
        doctor_experience = DoctorExperience.objects.filter(user=user)
        doctor_licensing = DoctorLicensing.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # If user profile doesn't exist, redirect to a setup page
        messages.warning(request, "You need to set up your profile.")
        return redirect('edit_doctor_profile')  # Redirect to profile setup
    except DoctorContactInfo.DoesNotExist:
        # If contact info doesn't exist, show a message
        messages.warning(request, "You need to provide your contact information.")
        return redirect('edit_doctor_profile')
    except DoctorLicensing.DoesNotExist:
        # If licensing doesn't exist, show a message
        messages.warning(request, "Please add your licensing details.")
        return redirect('edit_doctor_profile')

    # Set default profile picture if not provided
    profile_picture = user_profile.profile_picture.url if user_profile.profile_picture else 'assets/img/user.jpg'

    # Prepare context only if all required data is available
    context = {
        'user_profile': user_profile,
        'doctor_contact': doctor_contact,
        'doctor_education': doctor_education,
        'doctor_experience': doctor_experience,
        'doctor_licensing': doctor_licensing,
        'profile_picture': profile_picture,
    }

    return render(request, "accounts/doctor_profile.html", context)

@login_required
def edit_doctor_profile(request):
    user_profile = UserProfile.objects.get(user=request.user, usertype='doctor')
    
    try:
        # Fetch the doctor's contact info
        doctor_contact_info = DoctorContactInfo.objects.get(user=request.user)
    except DoctorContactInfo.DoesNotExist:
        doctor_contact_info = None

    try:
        doctor_education = DoctorEducation.objects.get(user=request.user)
    except DoctorEducation.DoesNotExist:
        doctor_education = None

    try:
        doctor_licensing = DoctorLicensing.objects.get(user=request.user)
    except DoctorLicensing.DoesNotExist:
        doctor_licensing = None

    doctor_experience = DoctorExperience.objects.filter(user=request.user)
    departments = Department.objects.all()

    if request.method == 'POST':
        # Handle date formats
        date_of_birth = request.POST['date_of_birth'].replace('/', '-')
        start_date = request.POST['start_date'].replace('/', '-')
        completion_date = request.POST['completion_date'].replace('/', '-')
        license_expiry = request.POST['license_expiry'].replace('/', '-')

        # Parse dates, with a fallback for empty dates
        date_of_birth = parse_date(date_of_birth)
        start_date = parse_date(start_date)
        completion_date = parse_date(completion_date)
        license_expiry = parse_date(license_expiry)

        # Save basic information
        user_profile.user.first_name = request.POST['first_name']
        user_profile.user.last_name = request.POST['last_name']
        user_profile.date_of_birth = date_of_birth
        user_profile.gender = request.POST['gender']

        if request.FILES.get('profile_picture'):
            user_profile.profile_picture = request.FILES['profile_picture']

        user_profile.user.save()
        user_profile.save()

        # Save contact info
        # Save contact info
        if doctor_contact_info:
            doctor_contact_info.address = request.POST['address']
            doctor_contact_info.county = request.POST['county']
            doctor_contact_info.country = request.POST['country']
            doctor_contact_info.phone_number = request.POST['phone_number']
            doctor_contact_info.emergency_number = request.POST['emergency_number']
            doctor_contact_info.save()
        else:
            # Create new DoctorContactInfo if it doesn't exist
            DoctorContactInfo.objects.create(
                user=request.user,
                address=request.POST['address'],
                county=request.POST['county'],
                country=request.POST['country'],
                phone_number=request.POST['phone_number'],
                emergency_number=request.POST['emergency_number']
            )


        specialization_id = request.POST['specialization']
        specialization = Department.objects.get(id=specialization_id)

        # Save or create education info
        if doctor_education:
            doctor_education.institution = request.POST['institution']
            doctor_education.award = request.POST['award']
            doctor_education.specialization = specialization  # Assign the Department instance
            doctor_education.start_date = start_date
            doctor_education.completion_date = completion_date
            doctor_education.save()
        else:
            DoctorEducation.objects.create(
                user=request.user,
                institution=request.POST['institution'],
                award=request.POST['award'],
                specialization=specialization,
                start_date=start_date,
                completion_date=completion_date,
            )

        # Save licensing info if it exists, otherwise create a new one
        if doctor_licensing:
            doctor_licensing.license_number = request.POST['license_number']
            doctor_licensing.license_issuing_authority = request.POST['license_issuing_authority']
            doctor_licensing.license_expiry = license_expiry
            doctor_licensing.save()
        else:
            DoctorLicensing.objects.create(
                user=request.user,
                license_number=request.POST['license_number'],
                license_issuing_authority=request.POST['license_issuing_authority'],
                license_expiry=license_expiry,
            )

        # Handle multiple experiences
        number_of_experiences = len(doctor_experience)
        for i in range(1, number_of_experiences + 1):
            company_name = request.POST.get(f'company_name_{i}')
            location = request.POST.get(f'location_{i}')
            job_position = request.POST.get(f'job_position_{i}')
            period_from = request.POST.get(f'period_from_{i}')
            period_to = request.POST.get(f'period_to_{i}')
            experience_id = request.POST.get(f'experience_id_{i}')  # Get the experience ID

            # If company_name exists, check if it's updating or creating
            if company_name:
                if experience_id:  # Update existing experience if ID is present
                    experience = DoctorExperience.objects.get(id=experience_id, user=request.user)
                    experience.company_name = company_name
                    experience.location = location
                    experience.job_position = job_position
                    experience.period_from = period_from
                    experience.period_to = period_to
                    experience.save()
                else:  # Create a new experience if no experience_id
                    DoctorExperience.objects.create(
                        user=request.user,
                        company_name=company_name,
                        location=location,
                        job_position=job_position,
                        period_from=period_from,
                        period_to=period_to,
                    )


        # Redirect to the profile view
        return redirect('doctor_profile')

    return render(request, 'accounts/edit_doctor_profile.html', {
        'doctor_userprofile': user_profile,
        'doctor_contact_info': doctor_contact_info,
        'doctor_education': doctor_education,
        'doctor_licensing': doctor_licensing,
        'doctor_experience': doctor_experience,
        'departments': departments,
    })


def delete_experience(request):
    if request.method == 'POST':
        experience_id = request.POST.get('experience_id')
        
        try:
            experience = DoctorExperience.objects.get(id=experience_id, user=request.user)
            experience.delete()
        except DoctorExperience.DoesNotExist:
            raise Http404("Experience not found.")
        
    return redirect('edit_doctor_profile')

def edit_patient_profile(request):
    return render(request, "accounts/edit_patient_profile.html")

def view_patient_profile(request):
    user = request.user

    # Initialize variables as None
    patient_contact_info = None
    patient_medical_info = None
    patient_insurance_info = None
    patient_social_info = None

    # Get user profile (assuming this exists)
    user_profile = get_object_or_404(UserProfile, user=user)

    try:
        # Attempt to get the patient's contact info
        patient_contact_info = PatientContactInfo.objects.get(user=user)
    except PatientContactInfo.DoesNotExist:
        pass

    try:
        # Attempt to get the patient's medical info
        patient_medical_info = PatientMedicalInfo.objects.get(user=user)
    except PatientMedicalInfo.DoesNotExist:
        pass

    try:
        # Attempt to get the patient's insurance info
        patient_insurance_info = PatientInsuranceInfo.objects.get(user=user)
    except PatientInsuranceInfo.DoesNotExist:
        pass

    try:
        # Attempt to get the patient's social info
        patient_social_info = PatientSocialInfo.objects.get(user=user)
    except PatientSocialInfo.DoesNotExist:
        pass

    context = {
        'user_profile': user_profile,
        'patient_contact_info': patient_contact_info,
        'patient_medical_info': patient_medical_info,
        'patient_insurance_info': patient_insurance_info,
        'patient_social_info': patient_social_info,
    }

    return render(request, "accounts/view_patient_profile.html", context)