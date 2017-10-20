"""sandboxmgt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.conf.urls import url
from . import views, views_register


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^cookies$', TemplateView.as_view(
        template_name='cookies.html'), name='cookies'),
    url(r'^register/?$', RedirectView.as_view(url='/register/github-intro', permanent=False), name='register'),
    url(r'^register/github-intro$', views_register.github_intro, name='register_github_intro'),
    url(r'^register/email$', views_register.email, name='register_email'),
    url(r'^register/email-validate-request$', views_register.email_validate_request, name='register_email_validate_request'),
    url(r'^register/email-validate$', views_register.email_validate, name='register_email_validate'),
    url(r'^register/data-security-classification$', views_register.data_security_classification, name='register_data_security_classification'),
    url(r'^register/data-security-classification-advice$', views_register.data_security_classification_advice, name='register_data_security_classification_advice'),
    url(r'^register/ethics$', views_register.ethics, name='register_ethics'),
    url(r'^register/terms$', views_register.terms, name='register_terms'),
    url(r'^my-sandbox$', views.my_sandbox, name='my_sandbox'),
    url(r'^admin$', views.admin, name='admin'),
    url(r'^deploy-start$', views.deploy_start, name='deploy_start'),
    url(r'^deploy$', views.deploy, name='deploy'),
    url(r'^delete-sandbox$', views.delete_sandbox, name='delete_sandbox'),
    url(r'^delete$', views.delete, name='delete'),
]
