from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def ipo_home(request):
    return render(request, "ipo/home.html")