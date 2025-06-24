from django.http import HttpResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import status_service, administrator_server
import logging

log_administrator = logging.getLogger('serverAdministrator')

@login_request
def server_Administrator(request: HttpResponse)  -> HttpResponse:
    """
    Funcion encargada de administrar los servicios y lo que se ordena hacer, asi como de regresar el estado de estos
    Args:
        request (HttpResponse)

    Returns:
        HttpResponse: render de la pagina que muestra los estados de los servicios
    """
    t = 'monitoreo.html'
    servers = models.servers.objects.all()
    servers_Name = []

    context = {
        'servers': servers_Name,
        'services': {},
        'selected_server': None,
        'name_server': None,
    }


    for server in servers:
        servers_Name.append(server.name)

    if request.method == 'GET':
        return render(request, t, {'servers': servers_Name})
    elif request.method == 'POST':
        name_server = request.POST.get('server_name', '').strip()
        name_service = request.POST.get('service_name', '').strip()
        option = request.POST.get('option', '').strip()
        service_status = {}
        context['selected_server'] = name_server
        context['name_server'] = name_server

        if not option:
            try:
                server_unic = models.servers.objects.get(name = name_server)
                services = models.services.objects.filter(server = server_unic)
                for service in services:
                    name = service.name
                    status = status_service(server_unic.ip_address, service.name)
                    service_status[name] = status
                context['services'] = service_status
                log_administrator.info('Se recupero la informacion correctamente')
                return render(request, t, context)
            except:
                log_administrator.error('Error al  informacion correctamente')
                return render(request, t, context)
        else:
            if not name_service:
                log_administrator.error('Se paso servicio vacio')
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
                        log_administrator.info('Se modifico el estado del servicio correctamente')
                        return render(request, t, context)
                    else:
                        log_administrator.error('Error al modificar el estado del servicio')
                        return render(request, t, context)
                else:
                    log_administrator.error('Se paso opcion incorrecta')
                    return render(request, t, context)
