from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html') 

def drivers_dashboard(request):
    return render(request, 'drivers_dashboard.html')

def riders_dashboard(request):
    return render(request, 'riders_dashboard.html')

