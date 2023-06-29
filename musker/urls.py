from django.urls import path

from musker.views import home, profile_list, profile, MeepCreateView, MeepListView

urlpatterns = [
    path("", home, name='home'),
    path("profile_list/", profile_list, name='profile_list'),
    # path("profile/<int:pk>/", ProfileDetailView.as_view(), name='profile'),
    path("profile/<int:pk>/", profile, name='profile'),
    path("add_meeps/", MeepCreateView.as_view(), name='add_meeps'),
    path("meep_list/", MeepListView.as_view(), name='meep_list'),
]