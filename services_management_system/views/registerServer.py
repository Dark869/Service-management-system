from django.http import HttpResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
import logging
from services_management_system.utils.ssh import register_server

ERROR_MESSAGES = {
    'empty_fields': 'Los campos no puden ir vacios',
    'existen_fields': 'Parametros existentes:',
    'register_failed': 'Registro fallido'
}

EXISTO_MESSAGES = {
    'exito': 'Registro exitoso.'
}

server_registration_log = logging.getLogger('registerServer')

@login_request
def register_Server(request: HttpResponse)  -> HttpResponse:
    """
    Funcion encargada del proceso de registrar servidor.
    Args:
        request (HttpResponse)

    Returns:
        HttpResponse: render de la pagina que muestra si fue un exito o si fallo 
    """
    t = 'registerServer.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        name = request.POST.get('name', '').strip()
        ip = request.POST.get('IP', '').strip()
        password = request.POST.get('password', '').strip()
        errores = []
        exito = []
        if not name or not ip or not password:
            server_registration_log.info("Se pasaron parametros vacios")
            errores.append(ERROR_MESSAGES['empty_fields'])
            return render(request, t, {'errores': errores})
        
        if models.servers.objects.filter(name = name).exists() or models.servers.objects.filter(ip_address = ip).exists():
            server_registration_log.info("Intento de registro fallido por parametros existentes")
            errores.append(ERROR_MESSAGES['existen_fields'])
            return render(request, t, {'errores': errores})
        
        if register_server(ip, password):
            try:
                server = models.servers(name = name, ip_address = ip)
                server.save()
                server_registration_log.info(f"Registro de servidor con IP:{ip} exitoso")
                exito.append(EXISTO_MESSAGES['exito'])
                return render(request, t, {'correctos': exito})
            except:
                server_registration_log.error(f"Fallo al registrar el servidor con la IP: {ip}. Revisa los logs de SSH")
                errores.append(ERROR_MESSAGES['register_failed'])
                return render(request, t, {'errores': errores})
        else:
            server_registration_log.error(f"Fallo al registrar el servidor con la IP: {ip}. Revisa los logs de SSH")
            errores.append(ERROR_MESSAGES['register_failed'])
            return render(request, t, {'errores': errores})
            
        
