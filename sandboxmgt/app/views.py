from django.shortcuts import render
from django.http import HttpResponseRedirect


from .forms import RequestForm


def home(request):
    return render(request, "home.html", {})


def request_sandbox(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            # TODO: Save form in the database
            # ...

            # TODO: Send form data by email
            # ...

            # Redirect user to a thank you page
            return HttpResponseRedirect('/thanks/')

    else:
        form = RequestForm()

    return render(request, 'request.html', {'form': form})
