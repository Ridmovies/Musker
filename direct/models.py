from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from musker.models import Profile


class Message(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    body = models.TextField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"from: {self.sender} to: {self.recipient} - {self.body}"


@receiver(post_save, sender=Message)
def direct_signal_message(sender, **kwargs):
    if kwargs['created']:
        print('direct message')
        instance = kwargs['instance']
        recipient_message_id = instance.recipient.id
        Profile.objects.filter(id=recipient_message_id).update(new_messages=True)


# post_save.connect(direct_signal_message, sender=Message)