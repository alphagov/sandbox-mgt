from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient
from .forms import RequestForm


def home(request):
    return render(request, "home.html", {})


def request_sandbox(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            # Save form in the database
            #form.save()

            # Send form data by email
            personalisation = {
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

            # Redirect user to a thank you page
            return HttpResponseRedirect('/thanks')

    else:
        form = RequestForm()

    return render(request, 'request.html', {'form': form})
