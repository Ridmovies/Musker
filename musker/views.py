import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView
from taggit.models import Tag

from musker.forms import MeepForm, UserRegistrationForm, UserProfileUpdateForm, ProfilePicForm, CommentForm
from musker.models import Profile, Meep, Category, Comment, EmailVerification


def home(request):
    meeps = Meep.objects.all().order_by('-created_at')

    paginator = Paginator(meeps, 3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Home',
        'meeps': meeps,
        'page_obj': page_obj
        # 'categories': categories,
    }
    return render(request, 'home.html', context=context)


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        context = {
            "object_list": profiles,
            'title': 'Profiles',
        }
        return render(request, 'profile_list.html', context=context)
    else:
        messages.success(request, "You Must Be Logged In To View This Page...")
        return redirect('home')


def follows_list(request, pk):
    if request.user.is_authenticated:
        current_profile = Profile.objects.get(user_id=pk)
        follows_profiles = current_profile.follows.all()
        context = {"object_list": follows_profiles,
                   'title': 'Follows List'}
        return render(request, 'follows_list.html', context)
    else:
        messages.success(request, "You Must Be Logged In To View This Page...")
        return redirect('home')


def follow_by_list(request, pk):
    if request.user.is_authenticated:
        current_profile = Profile.objects.get(user_id=pk)
        follows_profiles = current_profile.followed_by.all()
        context = {"object_list": follows_profiles,
                   'title': 'follow_by_list'}
        return render(request, 'follow_by_list.html', context)
    else:
        messages.success(request, "You Must Be Logged In To View This Page...")
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
        messages.success(request, "You Must Be Logged In To View This Page...")
        return redirect('home')


def unfollow(request, pk):
    if request.user.is_authenticated:
        unfollow_profile = Profile.objects.get(user_id=pk)
        current_user_profile = request.user.profile
        # if request.method == "POST":
        current_user_profile.follows.remove(unfollow_profile)

        return redirect(request.META.get('HTTP_REFERER'))


class MeepCreateView(CreateView):
    model = Meep
    form_class = MeepForm
    template_name = 'meep_form.html'
    # fields = ['body']
    success_url = reverse_lazy('home')
    extra_context = {'title': 'Add Meep'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class BugReportMeepCreateView(CreateView):
    model = Meep
    fields = ['body', 'image']
    template_name = 'bug_report.html'
    success_url = reverse_lazy('home')
    extra_context = {'title': 'Bug Report'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.category = Category.objects.get(title='Bug Report')
        return super().form_valid(form)


class MeepListView(ListView):
    model = Meep
    template_name = 'meep_list.html'
    extra_context = {'title': 'Meep List'}


def meep_list_tag(request, tag_slug=None):
    meep_list = Meep.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
    meep_list = meep_list.filter(tags__in=[tag])
    return render(request,
                  'meep_list_tag.html',
                  {'object_list': meep_list,
                   'tag': tag})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You Have Been Logged In!  Get MEEPING!")
                return redirect('home')
            else:
                messages.success(request, "There was an error logging in. Please Try Again...")
                return redirect('login')

        else:
            messages.success(request, "Login or password not correct")
            return redirect('login')

    else:
        form = AuthenticationForm()
        context = {
            'title': 'Login',
            'form': form,
        }
        return render(request, 'login_form.html', context=context)


def user_logout(request):
   logout(request)
   return redirect('home')


def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "You have successfully registered! Wellcome!")
            if form.instance.email:
                expiration = now() + timedelta(hours=48)
                record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
                record.send_verification_email()
            return redirect('home')
        else:
            messages.error(request, form.errors)
            return redirect('registration')
    else:
        form = UserRegistrationForm()
        context = {
            'title': 'Registration',
            'form': form,
        }
        return render(request, 'registration.html', context=context)


class UserRegistrationCreateView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('home')


class UserProfileUpdateView(UpdateView):
    # form_class = UserProfileUpdateForm
    model = User
    fields = ['first_name']
    template_name = 'edit_profile.html'
    extra_context = {'title': 'Edit Profile'}
    success_url = reverse_lazy('home')


def edit_user_profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Profile Has Been Updated!")
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = UserProfileUpdateForm(instance=request.user)

    context = {
        'form': form,
        'title': 'Store - Profile',
    }
    return render(request, template_name='edit_profile.html', context=context)


# Combining two forms into one
def update_user(request):
    if request.user.is_authenticated:
        # current_user = User.objects.get(id=request.user.id)
        # profile_user = Profile.objects.get(user__id=request.user.id)
        # Get Forms
        user_form = UserProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            # login(request, current_user)
            messages.success(request, "Your Profile Has Been Updated!")
            return redirect('home')

        context = {
            'title': 'Edit Profile',
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, "edit_profile.html", context)
    else:
        messages.success(request, "You Must Be Logged In To View That Page...")
        return redirect('home')


@login_required
def meep_like(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if meep.likes.filter(id=request.user.id):
        meep.likes.remove(request.user)

    else:
        meep.likes.add(request.user)

    # return redirect(reverse('home'))
    return redirect(request.META.get('HTTP_REFERER'))  # Don't work on tests and url


def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if meep:
        return render(request, "show_meep.html", {'meep': meep})
    else:
        messages.success(request, "That Meep Does Not Exist...")
        return redirect('home')


@login_required
def delete_meep(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if meep.user == request.user:
        if meep:
            Meep.objects.filter(id=pk).delete()
            messages.success(request, "Meep deleted successfully.")
    else:
        messages.success(request, "You are trying to delete someone else's Meep.")

    return redirect(reverse('home'))
        # return redirect(request.META.get('HTTP_REFERER'))


@login_required
def edit_meep(request, pk):
    if get_object_or_404(Meep, id=pk).user == request.user:
        if request.method == 'POST':
            form = MeepForm(request.POST or None, request.FILES or None, instance=Meep.objects.get(id=pk))
            if form.is_valid():
                form.save()
                messages.success(request, "Your Meep Has Been Updated!")
                return redirect('home')
        else:
            form = MeepForm(instance=Meep.objects.get(id=pk))
            context = {
                'title': 'Edit Meep',
                'form': form,
            }
            return render(request, template_name='edit_meep.html', context=context)
    else:
        messages.success(request, "You do not have access rights")
        return redirect('home')


# class CategoryListView(ListView):
#     model = Category
#     template_name = 'category_list.html'


def category(request, pk=None):
    # categories = Category.objects.all()
    if pk:
        # if Meep.objects.filter(category=pk).exists():
        meeps = Meep.objects.filter(category=pk).order_by('-created_at')
    else:
        meeps = Meep.objects.all().order_by('-created_at')
    context = {
        'title': f'Category {meeps.first().category.title}',
        'meeps': meeps,
    }
    return render(request, template_name='show_category.html', context=context)


@login_required
def add_comment(request, pk):

    meep = Meep.objects.get(id=pk)

    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        form.instance.meep_id = pk
        form.instance.name = request.user
        if form.is_valid():
            form.save()

        return redirect('home')

    else:
        context = {
            'title': 'Add comment',
            'form': CommentForm(),
            'meep': meep,
        }
        return render(request, template_name='add_comment.html', context=context)


def track_map(request):

    context = {
        # 'link': "https://yandex.ru/maps/?um=constructor%3A8115b4801e192f0f310d90a031709042cfdabd93a849e93200bc047b9683e03f&source=constructorLink",
        'link': "https://yandex.ru/map-widget/v1/?um=constructor%3A8115b4801e192f0f310d90a031709042cfdabd93a849e93200bc047b9683e03f&amp;source=constructor",
        'title': 'Track Map',
    }
    return render(request, template_name='track_map.html', context=context)


def search_meep(request):
    if request.method == 'POST':
        search_value = request.POST['search']
        searched = Meep.objects.filter(body__contains=search_value)
        context = {
            'title': 'Search meep',
            'search_value': search_value,
            'searched': searched
        }
        return render(request, template_name='search_meep.html', context=context)

    else:
        context = {
            'title': 'Search meep',
        }
        return render(request, template_name='search_meep.html', context=context)


def search_user(request):
    if request.method == 'POST':
        search_value = request.POST['search']
        searched = User.objects.filter(username__contains=search_value)
        context = {
            'title': 'Search user',
            'search_value': search_value,
            'searched': searched
        }
        return render(request, template_name='search_user.html', context=context)

    else:
        context = {
            'title': 'Search user',
        }
        return render(request, template_name='search_user.html', context=context)


