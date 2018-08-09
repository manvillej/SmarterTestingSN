from django import forms
from .models import SNTest, SNObject

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


class ObjectTestRelationshipForm(forms.Form):
    sn_object = forms.ModelChoiceField(
            queryset=SNObject.objects.all(),)
    test = forms.ModelChoiceField(
            queryset=SNTest.objects.all(),)

    relationship = forms.CharField(max_length=400,  widget=forms.Textarea,)
