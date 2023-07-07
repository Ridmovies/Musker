from django.contrib.auth.decorators import login_required
from django.urls import path

from direct.views import direct, CreateDirectView, message_read, message_delete

urlpatterns = [
    path("messages/<int:pk>/", direct, name='direct'),
    path("message_read/<int:pk>/", message_read, name='message_read'),
    path("message_delete/<int:pk>/", message_delete, name='message_delete'),
    path("create_direct/<int:pk>", login_required(CreateDirectView.as_view()), name='create_direct'),

]
