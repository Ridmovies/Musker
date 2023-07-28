from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from django.utils.timezone import now
from taggit.managers import TaggableManager


class Category(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    follows = models.ManyToManyField(to='self',
                                     related_name='followed_by',
                                     symmetrical=False,
                                     blank=True)
    date_modified = models.DateTimeField(User, auto_now=True)
    profile_image = models.ImageField(blank=True, null=True, upload_to='images/')

    profile_bio = models.CharField(null=True, blank=True, max_length=500)
    homepage_link = models.CharField(null=True, blank=True, max_length=100)
    facebook_link = models.CharField(null=True, blank=True, max_length=100)
    instagram_link = models.CharField(null=True, blank=True, max_length=100)
    linkedin_link = models.CharField(null=True, blank=True, max_length=100)
    new_messages = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# Create Profile When New User Signs Up
# @receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        # Have the user follow themselves
        user_profile.follows.set([instance.profile.id])
        user_profile.save()


post_save.connect(create_profile, sender=User)


class Meep(models.Model):
    user = models.ForeignKey(
        User, related_name="meeps",
        on_delete=models.DO_NOTHING
        )
    body = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="meep_like", blank=True)
    category = models.ForeignKey(to=Category, default=1, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='meep/images/')
    tags = TaggableManager()

    # Keep track or count of likes
    def number_of_likes(self):
        return self.likes.count()

    def __str__(self):
        return(
            f"{self.user} "
            f"({self.created_at:%Y-%m-%d %H:%M}): "
            f"{self.body}..."
            )


class Comment(models.Model):
    meep = models.ForeignKey(Meep, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# class User(AbstractUser):
#     is_verified_email = models.BooleanField(default=False)


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    class Meta:
        verbose_name = 'Email verification'
        verbose_name_plural = 'Email verification'

    def __str__(self):
        return f'Email verification for {self.user.email}'


    # def send_verification_email(self):
    #     send_mail(
    #         "Subject here",
    #         "Here is the message.",
    #         "from@example.com",
    #         ["to@example.com"],
    #         fail_silently=False,
    #     )

    def send_verification_email(self):
        # link = reverse('users:email_verification', kwargs={'email': self.user.email, 'code': self.code})
        # verification_link = f'{settings.DOMAIN_NAME}{link}'
        verification_link = 'test'
        subject = f'verify account for {self.user.username}'
        message = f'verification link {verification_link}'
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return True if now() >= self.expiration else False

