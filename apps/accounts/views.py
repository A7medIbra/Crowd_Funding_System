from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import auth
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user
from typing import Protocol
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser
from .forms import RegistrationForm, LoginForm, ChangePasswordForm, ResetPasswordForm, EditProfileForm
from .tokens import account_activation_token
from .models import CustomUser


def home(request):
    return render(request, 'home.html')


def send_email_activation(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("registration/verify_email_message.html", {
        'request': request,
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('/')


# **************Create user(register)********************
def create_user(request):
    form = RegistrationForm()
    # if request.user.is_authenticated: 
    #     return redirect('/')
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            if request.FILES:
                user.profile_picture = form.cleaned_data["profile_picture"]
            user.save()
            email = form.cleaned_data.get('username')
            send_email_activation(request, user, email)
            return redirect('home')
    return render(request, 'registration/register.html', {'form': form})

# ***************login****************************
# def login_user(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         print(form.is_valid())
#         if form.is_valid():
#             # Authenticate user
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             print(username, password)
#             print(form.cleaned_data['username'])
#             print(form.cleaned_data['password'])
#             user = authenticate(request, username=username, password=password)
#             print(user)
#             if user is not None:
#                 print(user.is_active)
#                 if user.is_active is True:
#                     print(user.is_active)
#                     login(request, user)
#                     return redirect(reverse('profile'))
#                 else:
#                     if user.date_joined + timezone.timedelta(days=1) < timezone.now():
#                         send_email_activation(request, user, username)
#                         form.add_error(None,
#                                        'Account activation link expired. Resent activation link, please check your email.')
#                     else:
#                         form.add_error(None,
#                                        'Your account is not yet activated. Please check your email for activation instructions.')
#             else:
#                 form.add_error(None, 'Your email or password is incorrect.')
#     else:
#         form = LoginForm()
#     return render(request, 'registration/login.html', {'form': form})
# *****************************
def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            # Check if the user exists and the password is correct
            if user is not None and user.check_password(password):
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('profile'))
                else:
                    # User is not active
                    activation_deadline = user.date_joined + timezone.timedelta(days=1)
                    if activation_deadline < timezone.now():
                        send_email_activation(request, user, username)
                        form.add_error(None, 'Account activation link expired. Resent activation link, please check your email.')
                    else:
                        form.add_error(None, 'Your account is not yet activated. Please check your email for activation instructions.')
            else:
                # User doesn't exist or entered incorrect credentials
                form.add_error(None, 'Your email or password is incorrect.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})
# ***********logout*************
def logout_user(request):
    logout(request)
    url = reverse('home')
    return redirect(url)
#     return render(request, 'login.html')

def user_profile(request):
    user = get_user(request)
    print(user.id)
    user_data = get_object_or_404(CustomUser, pk=2)
    user.phone_number = user_data.phone_number
    user.profile_picture = user_data.profile_picture
    user.facebook_profile = user_data.facebook_profile
    user.birth_date = user_data.birth_date
    user.country = user_data.country
    print(user)

    return render(request, "profile/profile_page.html",
                  context={"User": user})


# @login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        if 'delete_account' in request.POST:
            return redirect('delete_account')
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'profile/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = ChangePasswordForm(user)
    return render(request, 'password/password_reset_confirm.html', {'form': form})


# @user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['username']
            associated_user = get_user_model().objects.filter(Q(username=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("password/password_reset_message.html", {
                    'request': request,
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.username])
                email.content_subtype = 'html'
                try:
                    email.send()
                    messages.success(request, "Password reset email has been sent.")
                    return redirect('login')
                except Exception as e:
                    messages.error(request, f"Failed to send reset password email. Error: {str(e)}")
            else:
                messages.error(request, "User with this email does not exist.")
        else:
            messages.error(request, "Invalid email address. Please enter a valid email.")
    else:
        form = ResetPasswordForm()
    return render(request, "password/password_reset.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ChangePasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in</b> now.")
                return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
        else:
            form = ChangePasswordForm(user)
        return render(request, 'password/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("/")

# @login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        password = request.POST.get('password')
        if user.check_password(password):
            user.delete()
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
    return render(request, 'delete_account.html')
