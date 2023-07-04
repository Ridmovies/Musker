from django.urls import path

from direct.views import direct


urlpatterns = [
    path("messages/<int:pk>/", direct, name='direct'),
]
