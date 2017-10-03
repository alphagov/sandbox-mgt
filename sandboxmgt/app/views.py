from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.urls import reverse

import requests
from notifications_python_client.notifications import NotificationsAPIClient

from .forms import RequestForm, AdminRequestForm, DeleteForm, RedeployForm
from .models import Request


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

            return save_request_form_and_start_deploy(
                form, request, send_email_notifications=True)
    else:
        form = RequestForm()

    return render(request, 'request.html', {'form': form})


@login_required
def delete_sandbox(request):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            return start_delete(form, request)
    else:
        form = DeleteForm()

    return render(request, 'my_sandbox.html', {'form': form})


@login_required
def redeploy_sandbox(request):
    if request.method == 'POST':
        form = RedeployForm(request.POST)
        if form.is_valid():
            return start_redeploy(form, request)
    else:
        form = RedeployForm()

    return render(request, 'my_sandbox.html', {'form': form})


def save_request_form_and_start_deploy(form, request,
                                       send_email_notifications):
    # Save form in the database
    form.save()

    # Save the deploy info in the session - the user is probably not
    # logged in, but it needs storing for the next page, where feedback
    # is given on the deployment.
    request.session['github'] = form.cleaned_data['github']
    request.session['name'] = form.cleaned_data['name']
    # hard code the app for now
    request.session['app'] = 'rstudio'
    request.session['send_email_notifications'] = True
    request.session.save()

    # Start the deploy
    data = dict(
        name=form.cleaned_data['name'],
        github=form.cleaned_data['github'],
        email=form.cleaned_data['email'],
        )
    try:
        send_request_to_deploy_box('api/deploy', post_json_data=data)
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)

    # Redirect user to the deploy waiting/updates page
    return HttpResponseRedirect('/deploy')


def start_delete(form, request):
    request.session['github'] = form.cleaned_data['github']
    request.session['app'] = form.cleaned_data['app']

    # Start the deploy
    data = dict(
            github=form.cleaned_data['github'],
            app=form.cleaned_data['app'],
        )
    try:
        send_request_to_deploy_box('api/delete', post_json_data=data)
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)

    # Redirect user to the deploy waiting/updates page
    return HttpResponseRedirect(reverse('delete'))


def start_redeploy(form, request):
    request.session['github'] = form.cleaned_data['github']
    request.session['app'] = form.cleaned_data['app']

    # Start the deploy
    data = dict(
            github=form.cleaned_data['github'],
            app=form.cleaned_data['app'],
        )
    try:
        send_request_to_deploy_box('api/redeploy', post_json_data=data)
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)

    # Redirect user to the deploy waiting/updates page
    return HttpResponseRedirect(reverse('redeploy'))


def user_is_admin(user):
    return user.groups.filter(name='admin').exists()


@login_required
def my_sandbox(request):
    return render(request, 'my_sandbox.html')


def deploy(request):
    try:
        github = request.session['github']
        app = request.session['app']
    except KeyError:
        return HttpResponse('Could not get details of the request. Has your '
                            'browser got cookies enabled?', status=400)
    # find out the status of the deploy
    try:
        response = send_request_to_deploy_box('api/pod-statuses')
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)
    pods = response.json()
    # e.g.
    # [{'app': 'rstudio',
    #   'error': False,
    #   'messages': '',
    #   'phase': 'Running',
    #   'status': 'Ready',
    #   'user': '<github-username>'},
    filtered_pods = [
        pod for pod in pods
        if pod['app'] == app and pod['user'] == github]
    # TODO get the correct user
    if not filtered_pods:
        pod = {'phase': 'Not started yet', 'status': '', 'messages': ''}
    else:
        pod = filtered_pods[0]
    if pod['status'] != 'Ready':
        return render(request, 'deploying.html', dict(app=app, pod_status=pod))
    else:
        return render(request, 'deployed.html', dict(app=app, pod_status=pod))


def delete(request):
    import ipdb; ipdb.set_trace()
    try:
        github = request.session['github']
        app = request.session['app']
    except KeyError:
        return HttpResponse('Could not get details of the request. Has your '
                            'browser got cookies enabled?', status=400)
    # find out the status of the deploy
    try:
        response = send_request_to_deploy_box('api/pod-statuses')
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)
    pods = response.json()

    filtered_pods = [
        pod for pod in pods
        if pod['app'] == app and pod['user'] == github]

    # TODO get the correct user
    if not filtered_pods:
        return render(request, 'deleted.html', dict(app=app))
    else:
        pod = filtered_pods[0]
        return render(request, 'deleting.html', dict(app=app, pod_status=pod))


def redeploy(request):
    try:
        github = request.session['github']
        app = request.session['app']
    except KeyError:
        return HttpResponse('Could not get details of the request. Has your '
                            'browser got cookies enabled?', status=400)
    # find out the status of the deploy
    try:
        response = send_request_to_deploy_box('api/pod-statuses')
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)
    pods = response.json()
    # e.g.
    # [{'app': 'rstudio',
    #   'error': False,
    #   'messages': '',
    #   'phase': 'Running',
    #   'status': 'Ready',
    #   'user': '<github-username>'},
    filtered_pods = [
        pod for pod in pods
        if pod['app'] == app and pod['user'] == github]
    # TODO get the correct user
    if not filtered_pods:
        pod = {'phase': 'Not started yet', 'status': '', 'messages': ''}
    else:
        pod = filtered_pods[0]
    if pod['status'] != 'Ready':
        return render(request, 'deploying.html', dict(app=app, pod_status=pod))
    else:
        return render(request, 'deployed.html', dict(app=app, pod_status=pod))


@user_passes_test(user_is_admin)
def admin(request):
    if request.method == 'POST':
        # form is v similar to the one in sandboxes
        form = AdminRequestForm(request.POST)
        if form.is_valid():
            return save_request_form_and_start_deploy(
                form, request, send_email_notifications=False)
    else:
        form = AdminRequestForm()

    try:
        response = send_request_to_deploy_box('api/pod-statuses')
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)
    sandboxes = response.json()
    populate_user_info(sandboxes)
    return render(request, 'admin.html',
                  {'sandboxes': sandboxes, 'form': form})


def send_request_to_deploy_box(url_path, post_json_data=None, kwargs=None):
    '''
    May raise requests.RequestException
    '''
    kwargs = kwargs or {}
    if settings.SANDBOX_DEPLOY_USERNAME:
        kwargs['auth'] = (settings.SANDBOX_DEPLOY_USERNAME,
                          settings.SANDBOX_DEPLOY_PASSWORD)
    url = settings.SANDBOX_DEPLOY_URL + url_path
    if not post_json_data:
        response = requests.get(url, **kwargs)
    else:
        response = requests.post(url, json=post_json_data, **kwargs)
    response.raise_for_status()
    return response


def populate_user_info(sandboxes):
    '''Adds the user details to the sandboxes supplied'''
    for sandbox in sandboxes:
        github = sandbox['user']
        try:
            user = Request.objects.filter(github=github).all().last()
        except Request.DoesNotExist:
            # sandbox was not created by this web app - could have been
            # command-line, or by a different copy of this web app connected to
            # the same k8s cluster.
            user = None
        if user:
            sandbox['name'] = user.name
