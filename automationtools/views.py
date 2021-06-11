from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth.decorators import login_required


# Create your views here.
def report_home(request):
    return render(request, "report_home.html", context={"test": "hello world"})
