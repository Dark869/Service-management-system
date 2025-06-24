from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import status_service
import logging

@login_request
def server_Administrator(request: HttpResponse)  -> HttpResponse:
    t = 'monitoreo.html'

    if request.method == 'GET':
        name_server = request.GET.get('server_name', '').strip()
        services_list = []

        if not name_server:
            return False

        server_unic = models.servers.objects.get(name = name_server)
        services = models.services.objects.filter(server = server_unic)

        for service in services:
            status = status_service(server_unic.ip_address, service.name)
            if status == "active":
                return JsonResponse({'status': "success", 'message': "active"})
            elif status == "inactive":
                return JsonResponse({'status': "error", 'message': "inactive"})
            elif status == "not-found":
                return JsonResponse({'status': "error", 'message': "not-found"})
            elif status == "unknown":
                return JsonResponse({'status': "error", 'message': "unknown"})
            elif status == "error":
                return JsonResponse({'status': "error", 'message': "error"})
            elif status == "No localizado":
                return JsonResponse({'status': "error", 'message': "No localizado"})
            else:
                return JsonResponse({'status': "error", 'message': "Fallo"})