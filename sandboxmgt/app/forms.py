from django import forms
from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        exclude = []

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)

        # required = True will check if the box is checked, because data will
        # only be submitted if it is checked.
        self.fields['agree'].required = True
