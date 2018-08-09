from django import forms
from .models import SNTest, SNObject
from django.contrib.auth.models import User

class UploadFileForm(forms.Form):
    file = forms.FileField()


class ObjectTestRelationshipForm(forms.Form):
    sn_object = forms.ModelChoiceField(
            queryset=SNObject.objects.all(),)
    test = forms.ModelChoiceField(
            queryset=SNTest.objects.all(),)

    relationship = forms.CharField(max_length=400,  widget=forms.Textarea,)

class UserForm(forms.ModelForm):
    # TODO: User form
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
