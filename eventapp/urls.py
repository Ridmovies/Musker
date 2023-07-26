from django.contrib.auth.decorators import login_required
from django.urls import path

from eventapp.views import event_home, EventCreateView, EventDeleteView, EventUpdateView

urlpatterns = [
    path("", event_home, name='event_home'),
    path("event_delete/<int:pk>/", EventDeleteView.as_view(), name='event_delete'),
    path("event_edit/<int:pk>/", EventUpdateView.as_view(), name='event_edit'),
    path("add_event/", login_required(EventCreateView.as_view()), name='add_event'),
]
