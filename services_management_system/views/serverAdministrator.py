from django.http import HttpResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import status_service, administrator_server
import logging

ERROR_MESSAGES = {
    'empty_fields': 'Los campos no puden ir vacios',
}

EXISTO_MESSAGES = {
    'exito': 'Servicio agregado correctamente'
}

@login_request
def serverAdministrator(request: HttpResponse)  -> HttpResponse:
    t = 'monitoreo.html'
    servers = models.servers.objects.all()
    serversName = []

    context = {
        'servers': serversName,
        'services': {},
        'selected_server': None,
    }


    for server in servers:
        serversName.append(server.name)

    if request.method == 'GET':
        return render(request, t, {'servers': serversName})
    elif request.method == 'POST':
        name_server = request.POST.get('server_name', '').strip()
        name_service = request.POST.get('service_name', '').strip()
        option = request.POST.get('option', '').strip()
        service_status = {}
        context['selected_server'] = name_server
        errores = []
        exito = []

        if not option:
            try:
                server_unic = models.servers.objects.get(name = name_server)
                services = models.services.objects.filter(server = server_unic)
                for service in services:
                    name = service.name
                    status = status_service(server_unic.ip_address, service.name)
                    service_status[name] = status
                context['services'] = service_status

                return render(request, t, context)
            except:
                errores.append(ERROR_MESSAGES['empty_fields'])
                return render(request, t, {'errores': errores})
        else:
            if not name_service:
                return render(request, t, context)
            else:
                if option == "start" or option == "stop" or option == "restart":
                    server_unic = models.servers.objects.get(name = name_server)
                    if administrator_server(server_unic.ip_address,name_service,option):
                        services = models.services.objects.filter(server = server_unic)
                        for service in services:
                            name = service.name
                            status = status_service(server_unic.ip_address, service.name)
                            service_status[name] = status
                        context['services'] = service_status
                        return render(request, t, context)
                    else:
                        return render(request, t, context)
                else:
                    return render(request, t, context)
