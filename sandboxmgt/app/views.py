import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST

import requests
from notifications_python_client.notifications import NotificationsAPIClient

from .forms import AdminRequestForm, DeleteForm
from .models import Request


# The rstudio pod is not ready when k8s says it is - the readinessProbe would
# ideally be improved. As a simple alternative we just wait before giving the
# user the link. Tests show it takes another 30s on average.
RSTUDIO_EXTRA_WARMUP_TIME = 45  # seconds

def home(request):
    return render(request, "home.html", {})


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


def _start_deploy(name, github, email, request, send_email_notifications):
    # Save the deploy info in the session - the user is probably not
    # logged in, but it needs storing for the next page, where feedback
    # is given on the deployment.
    request.session['github'] = github
    request.session['name'] = name
    # hard code the app for now
    request.session['app'] = 'rstudio'
    request.session['send_email_notifications'] = True
    request.session.save()

    # Start the deploy
    data = dict(
        name=name,
        github=github,
        email=email,
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
    request.session['then_redeploy'] = form.cleaned_data.get('then_redeploy')

    # Start the delete
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


def user_is_admin(user):
    return user.groups.filter(name='admin').exists()


@login_required
def my_sandbox(request):
    try:
        my_pods = get_pod_statuses(filter_user=request.user.username)
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)
    all_apps = ['rstudio']
    def get_pod_by_app(app):
        for pod in my_pods:
            if pod['app'] == app:
                return pod
    apps_and_pods = dict((app, get_pod_by_app(app)) for app in all_apps)
    return render(request, 'my_sandbox.html', dict(
                  apps_and_pods=apps_and_pods,
                  user=request.user.username))


def deploy(request):
    try:
        github = request.session['github']
        app = request.session['app']
    except KeyError:
        return HttpResponse('Could not get details of the request. Has your '
                            'browser got cookies enabled?', status=400)
    # find out the status of the deploy
    try:
        filtered_pods = get_pod_statuses(filter_app=app, filter_user=github)
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)
    # TODO get the correct user
    if not filtered_pods:
        pod = {'phase': 'Not started yet', 'status': '', 'messages': ''}
    else:
        pod = filtered_pods[0]
    age = datetime.datetime.now() - \
        datetime.datetime.strptime(pod['lastTransitionTime'],
                                   '%Y-%m-%dT%H:%M:%SZ')
    if pod['status'] != 'Ready' or \
            age < datetime.timedelta(seconds=RSTUDIO_EXTRA_WARMUP_TIME):
        return render(request, 'deploying.html', dict(app=app, pod_status=pod))
    else:
        return render(request, 'deployed.html', dict(app=app, pod_status=pod))


@login_required
def delete(request):
    try:
        github = request.session['github']
        app = request.session['app']
        then_redeploy = request.session.get('then_redeploy')
    except KeyError:
        return HttpResponse('Could not get details of the request. Has your '
                            'browser got cookies enabled?', status=400)
    # find out the status of the deploy
    try:
        filtered_pods = get_pod_statuses(filter_app=app, filter_user=github)
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)

    # TODO get the correct user
    if not filtered_pods:
        if then_redeploy:
            # Start the deploy. We put dummy values in name and email because
            # helm in the backend doesn't really use them to deploy a sandbox.
            data = dict(
                name='Redeploy',
                github=github,
                email='redeploy@sandbox.com',)
            try:
                send_request_to_deploy_box('api/deploy', post_json_data=data)
            except requests.RequestException as e:
                return HttpResponse(str(e), status=500)

            # Redirect user to the deploy waiting/updates page
            return HttpResponseRedirect('/deploy')
        else:
            return render(request, 'deleted.html', dict(app=app))
    else:
        pod = filtered_pods[0]
        return render(request, 'deleting.html', dict(app=app, pod_status=pod))


@user_passes_test(user_is_admin)
def admin(request):
    if request.method == 'POST':
        # form is v similar to the one in sandboxes
        form = AdminRequestForm(request.POST)
        if form.is_valid():
            # Save form in the database
            form.save()
            return _start_deploy(
                form.cleaned_data['name'], form.cleaned_data['github'],
                form.cleaned_data['email'], request,
                send_email_notifications=False)
    else:
        form = AdminRequestForm()

    try:
        sandboxes = get_pod_statuses()
    except requests.RequestException as e:
        return HttpResponse(str(e), status=500)
    populate_user_info(sandboxes)
    return render(request, 'admin.html',
                  {'sandboxes': sandboxes, 'form': form})


@require_POST
def deploy_start(request):
    # Passed-in parameters
    try:
        github = request.POST['github']
        # app not passed through (for now)
    except KeyError as e:
        return HttpResponse('Missing parameter: {}'.format(e), status=400)

    # Request table gives us the user's full name
    try:
        user = Request.objects.filter(github=github).all().last()
    except Request.DoesNotExist:
        # sandbox was not created by this web app - could have been
        # command-line, or by a different copy of this web app connected to
        # the same k8s cluster.
        return HttpResponse('User details not found. Fill in the "request" '
                            'form first.', status=400)
    name = user.name
    email = user.email

    return _start_deploy(name, github, email, request,
                         send_email_notifications=False)


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


def get_pod_statuses(filter_app=None, filter_user=None):
    '''May raise requests.RequestException'''
    response = send_request_to_deploy_box('api/pod-statuses')
    pods = response.json()
    # e.g.
    # [{'app': 'rstudio',
    #   'error': False,
    #   'messages': '',
    #   'phase': 'Running',
    #   'status': 'Ready',
    #   'user': '<github-username>'},

    def apply_filters(pod):
        if filter_user is not None and pod['user'] != filter_user:
            return False
        if filter_app is not None and pod['app'] != filter_app:
            return False
        return True

    return [pod for pod in pods
            if apply_filters(pod)]
