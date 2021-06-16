from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from operations.views import get_data


@login_required
def render_home(request):
    return render(request, "home.html", context={})


def get_dashboards(request):
    json_data = get_data(name="get_dashboards")[0][0]

    return HttpResponse(json_data, content_type="application/json")
