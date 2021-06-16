from django.shortcuts import render,redirect
from django.contrib import auth, messages
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from django.core.mail import send_mail
import uuid
from django.conf import settings

# Create your views here.
def login(request):
    """
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pass']
        user = auth.authenticate(username=u, password=p)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid Email or Password!')
            return redirect('login')
    """
    if request.method == 'POST':
        u = request.POST.get('uname')
        p = request.POST.get('pass')

        user_obj = User.objects.filter(username = u).first()
        if user_obj is None:
            messages.success(request, 'User not found.')
            return redirect('login')
        
        
        profile_obj = Profile.objects.filter(user = user_obj ).first()

        if not profile_obj.is_verified:
            messages.success(request, 'Profile is not verified check your mail.')
            return redirect('login')

        user = authenticate(username = u , password = p)
        if user is None:
            messages.success(request, 'Wrong password.')
            return redirect('login')
        
        if user is not None:
            auth.login(request, user)
        #login(request , user)
            return redirect('index')

    return render(request, 'login.html')

def signup(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('signup')
    if request.method == "POST":
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        try:
            if User.objects.filter(username = username).first():
                messages.success(request, 'Username is taken.')
                return redirect('signup')

            if User.objects.filter(email = email).first():
                messages.success(request, 'Email is taken.')
                return redirect('signup')
            
            user_obj = User(first_name=firstname, last_name=lastname, username=username, email=email, password=password)
            user_obj.set_password(password)
            user_obj.save()

            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user = user_obj , auth_token = auth_token)
            profile_obj.save()
            send_mail_after_registration(email , auth_token)
            return redirect('token_send')

        except Exception as e:
            print(e)
    return render(request, 'signup.html')

def logout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    auth.logout(request)
    return redirect('login')

def success(request):
    return render(request , 'success.html')

def error_page(request):
    return  render(request , 'error.html')

def token_send(request):
    return render(request , 'token_send.html')

def verify(request , auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
    

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('login')
        else:
            return redirect('error')
    except Exception as e:
        print(e)
        return redirect('/')

def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list )

def index(request):
    return render(request, 'index.html')