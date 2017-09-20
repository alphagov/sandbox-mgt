from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

import requests
from notifications_python_client.notifications import NotificationsAPIClient

from .forms import RequestForm


def home(request):
    return render(request, "home.html", {})


def request_sandbox(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            # Send form data by email
            personalisation = {
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'github': form.cleaned_data['github'],
                'message': form.cleaned_data['message']
            }
            notify_client = NotificationsAPIClient(settings.NOTIFY_API_KEY)
            response = notify_client.send_email_notification(
                email_address=settings.NOTIFY_RECIPIENT_EMAIL,
                template_id=settings.NOTIFY_EMAIL_TEMPLATE_ID,
                personalisation=personalisation,
                reference=None
            )

            # Save form in the database
            form.save()

            # Redirect user to a thank you page
            return HttpResponseRedirect('/thanks')

    else:
        form = RequestForm()

    return render(request, 'request.html', {'form': form})


def user_is_admin(user):
    return user.groups.filter(name='admin').exists()

@user_passes_test(user_is_admin)
def my_sandbox(request):
    return render(request, 'my_sandbox.html')

@user_passes_test(user_is_admin)
def sandboxes(request):
    kwargs = {}
    if settings.SANDBOX_DEPLOY_USERNAME:
        kwargs['auth'] = (settings.SANDBOX_DEPLOY_USERNAME,
                          settings.SANDBOX_DEPLOY_PASSWORD)
    try:
        response = requests.get(settings.SANDBOX_DEPLOY_URL + 'api/pod-statuses',
                                **kwargs)
        response.raise_for_status()
    except Exception as e:
        return HttpResponse(str(e), status=500)
    sandboxes = response.json()
    return render(request, 'pod_statuses.html', {'sandboxes': sandboxes})
