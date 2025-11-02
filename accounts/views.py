"""
Views for Accounts App - Registration, Login, Logout, Profile
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserRegistrationForm, CustomLoginForm
from .models import CustomUser


def register(request):
    """
    User registration view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = CustomUser.Role.USER  # Default role is USER
            user.save()
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = CustomUserRegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Register - Hackotsava 2025'
    }
    return render(request, 'accounts/register.html', context)


def custom_login(request):
    """
    Custom login view
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Redirect based on role
                if user.is_admin():
                    return redirect('admin_dashboard')
                else:
                    return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login - Hackotsava 2025'
    }
    return render(request, 'accounts/login.html', context)


def custom_logout(request):
    """
    Logout view
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile(request):
    """
    User profile view
    """
    context = {
        'page_title': 'My Profile - Hackotsava 2025'
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """
    Edit user profile
    """
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'page_title': 'Edit Profile - Hackotsava 2025'
    }
    return render(request, 'accounts/edit_profile.html', context)
