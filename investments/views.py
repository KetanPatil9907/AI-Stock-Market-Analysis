from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def money_planner(request):
    return render(request, "investments/home.html")