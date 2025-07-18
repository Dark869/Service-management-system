from django.http import HttpResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import verify_service
import logging

ERROR_MESSAGES = {
    'empty_fields': 'Los campos no puden ir vacios',
    'existen_fields': 'Parametros existentes:',
    'register_failed': 'Registro fallido',
    'service_notfound': 'Servicio no instalado en el servidor',
    'verify_faild': 'Servidor no verificado',
    'server_notfound': 'Servidor no registrado'
}

EXISTO_MESSAGES = {
    'exito': 'Servicio agregado correctamente'
}

service_registration_log = logging.getLogger('RegistroServicio')

@login_request
def register_Service(request: HttpResponse)  -> HttpResponse:
    """
    Funcion encargada de registrar servicios de los servidores
    Args:
        request (HttpResponse)

    Returns:
        HttpResponse: render de la pagina que muestra si fue un exito o si fallo 
    """
    t = 'registerService.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        name_Service = request.POST.get('nameservice', '').strip()
        name_Server = request.POST.get('nameserver', '').strip()
        errores = []
        exito = []

        if not name_Service or not name_Server:
            service_registration_log.info("Se pasaron parametros vacios")
            errores.append(ERROR_MESSAGES['empty_fields'])
            return render(request, t, {'errores': errores})

        if models.servers.objects.filter(name = name_Service).exists() and models.servers.objects.filter(name = name_Server).exists():
            service_registration_log.info("Intento fallido, servicio ya registrado")
            errores.append(ERROR_MESSAGES['existen_fields'])
            return render(request, t, {'errores': errores})
        
        try:
            server = models.servers.objects.get(name=name_Server)
            if verify_service(name_Service, server.ip_address):
                try:
                    service = models.services(name = name_Service, server = server)
                    service.save()
                    service_registration_log.info(f"Registro se servicio {name_Service} exitoso para el server {name_Server}")
                    exito.append(EXISTO_MESSAGES['exito'])
                    return render(request, t, {'correctos': exito})
                except:
                    service_registration_log.error("Registro de servicio fallido. Verificar en log de SSH")
                    errores.append(ERROR_MESSAGES['register_failed'])
                    return render(request, t, {'errores': errores})
            else:
                service_registration_log.error("Fallo al registrar el servicio por servicio no instalado. Revisa los logs de SSH")
                errores.append(ERROR_MESSAGES['service_notfound'])
                return render(request, t, {'errores': errores})
        except:
            service_registration_log.error(f"Server {name_Server} no registrado")
            errores.append(ERROR_MESSAGES['server_notfound'])
            return render(request, t, {'errores': errores})