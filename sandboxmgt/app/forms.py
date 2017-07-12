from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Request


def validate_gov_email(value):
    if value.endswith('.gov.uk') is False:
        raise ValidationError(
            _('%(value)s is not a valid gov.uk email address'),
            params={'value': value},
        )


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        exclude = []

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)

        self.fields['name'].required = True
        # required = True will check if the box is checked, because data will
        # only be submitted if it is checked.
        self.fields['agree'].required = True
        self.fields['email'].validators.append(validate_gov_email)
