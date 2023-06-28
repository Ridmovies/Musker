from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from musker.models import Profile


def home(request):
    context = {'title': 'Home'}
    return render(request, 'home.html', context=context)


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"object_list": profiles})
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "profile.html"


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        context = {'profile': profile}
        return render(request, 'profile.html', context=context)
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')

        # meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")
        #
        # # Post Form logic
        # if request.method == "POST":
        #     # Get current user
        #     current_user_profile = request.user.profile
        #     # Get form data
        #     action = request.POST['follow']
        #     # Decide to follow or unfollow
        #     if action == "unfollow":
        #         current_user_profile.follows.remove(profile)
        #     elif action == "follow":
        #         current_user_profile.follows.add(profile)
        #     # Save the profile
        #     current_user_profile.save()

