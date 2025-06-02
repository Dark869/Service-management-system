from django.http import HttpResponse
from django.shortcuts import render
from services_management_system.middlewares.loginRequest import login_request

@login_request
def index(request: HttpResponse) -> HttpResponse:
    return render(request, 'pagesProtected.html')