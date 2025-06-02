from django.http import HttpResponse
from django.shortcuts import render
from services_management_system.middlewares.loginRequest import twofa_verified

@twofa_verified
def index(request: HttpResponse) -> HttpResponse:
    return render(request, 'index.html')

def plantilla(request: HttpResponse) -> HttpResponse:
    return render(request, 'monitor.html')
