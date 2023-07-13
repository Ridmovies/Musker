from django.contrib.auth.models import User
from django.db import models


class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} - {self.body}'

