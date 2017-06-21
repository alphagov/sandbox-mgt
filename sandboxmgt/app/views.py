from django.shortcuts import render
from django.http import HttpResponseRedirect


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('my_tasks'))

    return render(request, "home.html", {})


def request_sandbox(request):
    return render(request, "request.html", {})
