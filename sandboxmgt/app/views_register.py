from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse

import requests

from .forms import EmailForm
from .views import _start_deploy, get_pod_statuses


def github_intro(request):
    return render(request, 'register/github_intro.html', {})

@login_required
def email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            # TODO save the email address in the user

            # Send form data by email
            personalisation = {
                'email': form.cleaned_data['email'],
            }
            # TODO
            # notify_client = NotificationsAPIClient(settings.NOTIFY_API_KEY)
            # response = notify_client.send_email_notification(
            #     email_address=settings.NOTIFY_RECIPIENT_EMAIL,
            #     template_id=settings.NOTIFY_EMAIL_TEMPLATE_ID,
            #     personalisation=personalisation,
            #     reference=None
            # )

        return HttpResponseRedirect(reverse('register_email_validate_request'))
    return render(request, "register/email.html", {})

@login_required
def email_validate_request(request):
    return render(request, 'register/email_validate_request.html', {})

@login_required
def email_validate(request):
    return render(request, 'register/email_validate.html', {})

@login_required
def data_(request):
    return render(request, 'register/ethics.html', {})

@login_required
def data_security_classification(request):
    if request.method == 'POST':
        request.session['data_security_classification'] = request.POST['radio-group']
        return HttpResponseRedirect(reverse('register_data_security_classification_advice' ))
    return render(request, 'register/data_security_classification.html', {})

@login_required
def data_security_classification_advice(request):
    return render(request, 'register/data_security_classification_advice.html', {
        'data_security_classification': request.session['data_security_classification'],
        })

@login_required
def ethics(request):
    if request.method == 'POST':
        if request.POST.get('agree') == 'true':
            return HttpResponseRedirect(reverse('register_terms'))
    return render(request, 'register/ethics.html', {})

@login_required
def terms(request):
    if request.method == 'POST':
        if request.POST['agree']:
            # has_user_already_got_rstudio_deployed?
            try:
                my_rstudio = get_pod_statuses(filter_user=request.user.username,
                                              filter_app='rstudio')
            except requests.RequestException as e:
                return HttpResponse(str(e), status=500)
            if my_rstudio:
                request.session['github'] = request.user.username
                request.session['app'] = 'rstudio'
                return HttpResponseRedirect(reverse('deploy'))
            else:
                github = request.user.username
                email = request.user.email or 'fake_email@example.com'  # TODO
                return _start_deploy(
                    'fake name', github, email, request,
                    send_email_notifications=False)
    return render(request, 'register/terms.html', {})

@login_required
def data_ethics(request):
    return render(request, 'register/data_ethics.html', {})

@login_required
def agree_start(request):
    return render(request, 'register/agree_start.html', {})

