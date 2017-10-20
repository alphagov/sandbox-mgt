import re

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


def validate_email(value):
    # guard against errors like commas: john,smith@...
    # which screw up the helm command later on
    if not re.match('^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$', value):
        raise ValidationError(
            _('%(value)s is not a valid email address'),
            params={'value': value},
            )


def validate_github(value):
    # According to the form validation messages on Join Github page,
    # Github username may only contain alphanumeric characters or hyphens.
    bad_chars = re.findall('[^\w0-9-]', value)
    if bad_chars:
        raise ValidationError(
            _('Github user names should not contain these characters: '
              '%(values)s. Check your user name with Github.'),
            params={'values': repr(bad_chars)},
        )


class EmailForm(forms.Form):
    email = forms.CharField(label='email')

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)

        self.fields['email'].validators.extend([validate_email,
                                                validate_gov_email])


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
        self.fields['email'].validators.extend([validate_email,
                                                validate_gov_email])
        self.fields['github'].validators.append(validate_github)


class AdminRequestForm(RequestForm):

    def __init__(self, *args, **kwargs):
        super(AdminRequestForm, self).__init__(*args, **kwargs)

        # admin might be able to vouch for them, or not - best to be truthful
        # rather than constrain
        self.fields['agree'].required = False
        self.fields['message'].required = False


class DeleteForm(forms.Form):

    github = forms.CharField(max_length=255)
    app = forms.CharField(max_length=255)
    then_redeploy = forms.BooleanField(required=False)
