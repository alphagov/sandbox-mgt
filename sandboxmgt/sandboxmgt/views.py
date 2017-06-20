from django.http import HttpResponseRedirect
from django.shortcuts import render


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('my_tasks'))

    return render(request, "home.html", {})
