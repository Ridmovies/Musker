from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from musker.forms import MeepForm, UserLoginForm
from musker.models import Profile, Meep


def home(request):
    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request, ("Your Meep Has Posted!"))
                return redirect('home')

        meeps = Meep.objects.all().order_by('-created_at')
        context = {
            'title': 'Home',
            'meeps': meeps,
            'form': form,
        }
        return render(request, 'home.html', context=context)

    else:
        meeps = Meep.objects.all().order_by('-created_at')
        context = {
            'title': 'Home',
            'meeps': meeps,
        }
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
        meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")
        context = {'profile': profile, 'meeps': meeps}

        # Post Form logic
        if request.method == "POST":
            # Get current user
            current_user_profile = request.user.profile
            # Get form data
            action = request.POST['follow']
            # Decide to follow or unfollow
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            # Save the profile
            current_user_profile.save()

        return render(request, 'profile.html', context=context)
    else:
        messages.success(request, ("You Must Be Logged In To View This Page..."))
        return redirect('home')


class MeepCreateView(CreateView):
    model = Meep
    template_name = 'meep_form.html'
    fields = '__all__'
    success_url = reverse_lazy('home')


class MeepListView(ListView):
    model = Meep
    template_name = 'meep_list.html'
    extra_context = {'title': 'Meep List'}


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            print(request.POST)
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, ("You Have Been Logged In!  Get MEEPING!"))
                return redirect('home')
            else:
                messages.success(request, ("There was an error logging in. Please Try Again..."))
                return redirect('login')

        else:
            messages.success(request, ("Login or password not correct"))
            return redirect('login')

    else:
        form = UserLoginForm()
        context = {
            'title': 'Login',
            'form': form,
        }
        return render(request, 'login_form.html', context=context)


def user_logout(request):
   logout(request)
   return redirect('home')






