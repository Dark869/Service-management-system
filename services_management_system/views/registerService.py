from django.http import HttpResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import verify_fingerprint, verify_service
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
def registerService(request: HttpResponse)  -> HttpResponse:
    t = 'registerService.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        nameService = request.POST.get('nameservice', '').strip()
        nameServer = request.POST.get('nameserver', '').strip()
        errores = []
        exito = []

        if not nameService or not nameServer:
            service_registration_log.info("Se pasaron parametros vacios")
            errores.append(ERROR_MESSAGES['empty_fields'])
            return render(request, t, {'errores': errores})

        if models.servers.objects.filter(name = nameService).exists() and models.servers.objects.filter(name = nameServer).exists():
            service_registration_log.info("Intento fallido, servicio ya registrado")
            errores.append(ERROR_MESSAGES['existen_fields'])
            return render(request, t, {'errores': errores})
        
        try:
            server = models.servers.objects.get(name=nameServer)
            if verify_fingerprint(nameServer, server.ip_address):
                if verify_service(nameServer,nameService, server.ip_address):
                    try:
                        service = models.services(name = nameService, server = server)
                        service.save()
                        service_registration_log.info(f"Registro se servicio {nameService} exitoso para el server {nameServer}")
                        exito.append(EXISTO_MESSAGES['exito'])
                        return render(request, t, {'correctos': exito})
                    except:
                        service_registration_log.error(f"Registro de servicio fallido. Verificar en log de SSH")
                        errores.append(ERROR_MESSAGES['register_failed'])
                        return render(request, t, {'errores': errores})
                else:
                    service_registration_log.error(f"Fallo al registrar el servicio por servicio no instalado. Revisa los logs de SSH")
                    errores.append(ERROR_MESSAGES['service_notfound'])
                    return render(request, t, {'errores': errores})
            else:
                service_registration_log.error(f"Servidor {nameServer} no registrado")
                errores.append(ERROR_MESSAGES['verify_faild'])
                return render(request, t, {'errores': errores})
        except:
            service_registration_log.error(f"Server {nameServer} no registrado")
            errores.append(ERROR_MESSAGES['server_notfound'])
            return render(request, t, {'errores': errores})