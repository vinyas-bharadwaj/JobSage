from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        
        messages.error(request, 'Invalid username or password')
        return redirect('/auth/login')

    return render(request, 'auth/login.html', context={})

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "The passwords do not match!")
            return redirect('/auth/signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Account with that username already exists")
            return redirect('/auth/signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Account with that email already exists")
            return redirect('/auth/signup')
        
        # Create user and set email
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Authenticate the user first, then login
        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            messages.success(request, f"Welcome to JobSage, {username}!")
            return redirect('/')
        else:
            # Fallback: redirect to login if authentication fails
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('/auth/login')

    return render(request, 'auth/signup.html', context={})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('/auth/login')