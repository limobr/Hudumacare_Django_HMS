from django.shortcuts import redirect, render
from accounts.models import UserProfile
from landing.models import Contact
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    total_patients = UserProfile.objects.filter(usertype='patient').count()
    
    return render(request, "landing/index.html", {'total_patients': total_patients})

@login_required
def dashboard_redirect(request):
    # Assuming you have a user profile with usertype
    user_profile = UserProfile.objects.get(user=request.user)

    # Redirect to respective dashboard based on usertype
    if user_profile.usertype == 'admin':
        return redirect('admin_dashboard')
    elif user_profile.usertype == 'doctor':
        return redirect('doctor_dashboard')
    elif user_profile.usertype == 'patient':
        return redirect('patient_dashboard')
    else:
        return redirect('home')
    
def about(request):
    return render(request, "landing/about.html")

def contact(request):
    if request.method == 'POST':
        # Capture the form data and save it to the database
        new_contact = Contact(
            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message']
        )
        new_contact.save()
        
        # Render the page with a success flag
        return render(request, "landing/contact.html", {'form_submitted': True})
    
    # Render the page normally if it's a GET request
    return render(request, "landing/contact.html")



def gallery(request):
    return render(request, "landing/gallery.html")


def services(request):
    return render(request, "landing/services.html")