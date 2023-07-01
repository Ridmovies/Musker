from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from musker.models import Meep


class MeepForm(forms.ModelForm):
    body = forms.CharField(required=True,
                           widget=forms.widgets.Textarea(
                               attrs={
                                   "placeholder": "Enter Your Musker Meep!",
                                   "class": "form-control",
                               }
                           ),
                           label="",
                           )

    class Meta:
        model = Meep
        fields = ['body']


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


