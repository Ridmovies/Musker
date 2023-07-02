from django.urls import path

from musker.views import home, profile_list, profile, MeepCreateView, MeepListView, user_login, user_logout, \
    user_registration, UserProfileUpdateView, edit_user_profile, update_user

urlpatterns = [
    path("", home, name='home'),
    path("profile_list/", profile_list, name='profile_list'),
    # path("profile/<int:pk>/", ProfileDetailView.as_view(), name='profile'),
    path("profile/<int:pk>/", profile, name='profile'),
    path("add_meeps/", MeepCreateView.as_view(), name='add_meeps'),
    path("meep_list/", MeepListView.as_view(), name='meep_list'),
    path("login/", user_login, name='login'),
    path("logout/", user_logout, name='logout'),
    path("registration/", user_registration, name='registration'),
    # path("edit_profile/<int:pk>", UserProfileUpdateView.as_view(), name='edit_profile'),
    # path("edit_profile/", edit_user_profile, name='edit_profile'),
    path("edit_profile/", update_user, name='edit_profile'),

]