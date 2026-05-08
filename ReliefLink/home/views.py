# home/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import House
from django.contrib.auth import get_user_model
from .forms import ReliefSupplyForm
from django.db.models import F


User = get_user_model()

def can_add_user(user):
    return user.has_perm('home.can_add_user')

def can_remove_user(user):
    return user.has_perm('home.can_remove_user')


def index(request):
    return render(request, 'home/index.html')

def service(request):
    return render(request, 'home/service.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        subject = f"New Contact Form Submission from {name}"
        message_body = (
            f"Dear Admin,\n\n"
            f"You have received a new message from the contact form on your website.\n\n"
            f"Details:\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Message:\n{message}\n\n"
            f"Best regards,\n"
            f"ReliefLink Team"
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [settings.CONTACT_EMAIL]

        try:
            send_mail(subject, message_body, from_email, recipient_list)
            return render(request, 'home/contact_success.html')
        except Exception as e:
            return render(request, 'home/contact.html', {'error': 'Error sending email. Please try again later.'})

    return render(request, 'home/contact.html')


@login_required
def dashboard(request):
    user = request.user
    role = user.user_type
    if role == 'DivisionalCommissioner':
        return redirect('divisionalcommissioner_dashboard')
    
    elif role == 'Admin':
        return redirect('admin_dashboard')
    
    elif role == 'DeputyCommissioner':
        return redirect('deputycommissioner_dashboard')
    
    elif role == 'UNO':
        return redirect('uno_dashboard')
    
    elif role == 'UnionChairman':
        return redirect('unionchairman_dashboard')
    
    elif role == 'WardMember':
        return redirect('wardmember_dashboard')
    
    elif role == 'Public':
        return redirect('public_dashboard')
    
@login_required
def admin_dashboard(request):
    data = User.objects.filter(user_type='DivisionalCommissioner')
    return render(request, 'home/admin_dashboard.html', {'data': data})

@login_required
def divisionalcommissioner_dashboard(request):
    division = request.user.division
    deputycommissioners = User.objects.filter(user_type='DeputyCommissioner', district__division = division)

    return render(request, 'home/divisionalcommissioner_dashboard.html', {'deputycommissioners':deputycommissioners, 'division':division})

@login_required
def deputycommissioner_dashboard(request):
    district = request.user.district
    unos = User.objects.filter(user_type='UNO', upazila__district = district)

    return render(request, 'home/deputycommissioner_dashboard.html', {'unos': unos, 'district': district})


@login_required
def uno_dashboard(request):
    upazila = request.user.upazila
    unionchairmans = User.objects.filter(user_type='UnionChairman', union__upazila = upazila)

    return render(request, 'home/uno_dashboard.html', {'unionchairmans':unionchairmans, 'upazila': upazila})

@login_required
def unionchairman_dashboard(request):
    union = request.user.union
    wardmembers = User.objects.filter(user_type='WardMember', ward__union = union)

    return render(request, 'home/unionchairman_dashboard.html', {'wardmembers':wardmembers, 'union': union})

@login_required
def wardmember_dashboard(request):
    ward = request.user.ward
    houses = House.objects.filter(ward=ward)
    
    return render(request, 'home/wardmember_dashboard.html', {'houses': houses, 'ward': ward})


@login_required
def public_dashboard(request):
    return render(request, 'home/public_dashboard.html')


def get_house_details(house_id):
    house = get_object_or_404(House.objects.select_related(
        'ward__union__upazila__district__division'
    ), id=house_id)
    return {
        "holding_number": house.holding_number,
        "ward": house.ward.name,
        "division": house.ward.union.upazila.district.division.name,
    }


@login_required
def update_flood_status(request):
    if request.method == 'POST':
        ward = request.user.ward
        is_flood = 'is_flood' in request.POST
        dry_food_demand = int(request.POST.get('dry_food', 0))

        if ward.is_flood != is_flood and is_flood == False:
            House.objects.filter(ward=ward).update(relief_demand = F('family_member'), dry_food_supply = 0, primary_food_supply = 0)
            ward.dry_food_supply = 0
            ward.primary_food_supply = 0

        ward.is_flood = is_flood
        ward.dry_food_demand_in_percentage = dry_food_demand
        ward.save()

        if is_flood:
            ward.propagate_flood_status()
        else:
            ward.propagate_flood_remove_status()
        return redirect('dashboard')
    
@login_required
def relief_supply(request, house_id):
    house = House.objects.get(id=house_id)
    if request.method == "POST":
        form = ReliefSupplyForm(request.POST)
        if form.is_valid():
            relief_supply = form.cleaned_data['relief_supply']
            relief_type = form.cleaned_data['relief_type']
            if relief_supply > 0:
                house.relief_supply(relief_supply, relief_type)

        return redirect('dashboard')

    else:
        form = ReliefSupplyForm()

    content = {
        'house': house,
        'form': form,
    }
    return render(request, 'home/relief_supply.html', content)