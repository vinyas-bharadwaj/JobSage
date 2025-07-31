from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile

@login_required
def profile_view(request):
    """View and edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile fields
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.github_url = request.POST.get('github_url', '')
        profile.linkedin_url = request.POST.get('linkedin_url', '')
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
        'user': request.user,
    }
    
    return render(request, 'user_profile/profile.html', context)
