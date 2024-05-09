from django.views.decorators.csrf import csrf_protect
from payapp.forms import SendMoneyForm
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from register.forms import RegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from register.models import Account
from django.contrib.auth.forms import UserCreationForm
from .forms import AdminRegistrationForm



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test



@login_required(login_url='/webapps2024/login')
def home(request):
    try:
        account = Account.objects.get(user=request.user)  # This line is causing the error
        return render(request, 'webapps2024/register/home.html', {'balance': account.amount})
    except Account.DoesNotExist:
        # Handle the case where the account does not exist
        messages.error(request, "No account found for this user.")
        return render(request, 'webapps2024/register/home.html')

# Create your views here.
# @login_required(login_url='/webapps2024/login')
# @csrf_protect
# def home(request):
#     if request.user.is_authenticated:
#         account = Account.objects.get(user_id=request.user.id)
#         return render(request, 'webapps2024/register/home.html', {'balance': account.amount})
#     return render(request, 'webapps2024/register/home.html')


@csrf_protect
def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = RegisterForm()
    return render(request, "webapps2024/register/registration.html", {"register_user": form})


@csrf_protect
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "webapps2024/register/login.html", {"login_user": form})


@login_required(login_url='/webapps2024/login')
def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")





# Helper function to check if user is superuser
def is_superuser(user):
    return user.is_authenticated and user.is_superuser



@login_required
@user_passes_test(is_superuser)
def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Admin should be a staff
            user.is_superuser = True  # Optionally make the user a superuser
            user.save()
            return redirect('admin_dashboard')  # Redirect to the admin dashboard
        else:
            # If the form is not valid, render the form again with errors
            return render(request, 'webapps2024/register/admin_registration.html', {'form': form})
    else:
        form = AdminRegistrationForm()
        return render(request, 'webapps2024/register/admin_registration.html', {'form': form})









# @login_required
# @user_passes_test(is_superuser)
# def register_admin(request):
#     if request.method == 'POST':
#         form = AdminRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_staff = True  # or user.is_superuser = True depending on needs
#             user.save()
#             return redirect('admin_dashboard')  # Redirect after POST
#     else:
#         form = AdminRegistrationForm()
#     return render(request, 'webapps2024/register/admin_registration.html', {'form': form})




def admin_dashboard(request):
    # Ensure this template path is correct based on your templates directory structure
    return render(request, 'webapps2024/register/admin_dashboard.html')


def signup(request):
    # Your signup logic here
    return render(request, 'register/signup.html')
