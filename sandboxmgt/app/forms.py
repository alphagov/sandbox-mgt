from django import forms


class RequestForm(forms.Form):
    email = forms.CharField(required=True, max_length=255)
    github = forms.CharField(required=True, max_length=255)
    message = forms.CharField(required=True)
    agree = forms.BooleanField()
