import os
import base64

from django.conf import settings
from django.http import HttpResponse


def basic_challenge(realm='Restricted Access'):
    response = HttpResponse('Authorization Required')
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response


def basic_authenticate(authentication):
    (authmeth, auth) = authentication.split(' ', 1)
    if 'basic' != authmeth.lower():
        return None

    auth = base64.b64decode(bytes(auth, 'utf-8')).decode()

    username, password = auth.split(':', 1)
    auth_username = settings.HTTP_USERNAME
    auth_password = settings.HTTP_PASSWORD
    return username == auth_username and password == auth_password


class BasicAuthenticationMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not settings.HTTP_USERNAME:
            return response

        if 'HTTP_AUTHORIZATION' not in request.META:
            return basic_challenge()

        authenticated = basic_authenticate(request.META['HTTP_AUTHORIZATION'])
        if authenticated:
            return response

        return basic_challenge()
