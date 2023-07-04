from django import forms

from direct.models import Message


class DirectForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'


