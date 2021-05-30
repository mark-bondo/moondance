from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def render_home(request):
    return render(request, "home.html", context={})
