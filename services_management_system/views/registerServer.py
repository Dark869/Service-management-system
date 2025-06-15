from django.http import HttpResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import copy_key_serverRemote
from services_management_system.settings import LOGS_DIR
import logging

ERROR_MESSAGES = {
    'empty_fields': 'Los campos no puden ir vacios:',
    'ssh_field': 'Fallo registro:'
}

server_registration_log = logging.getLogger('registerServer')

@login_request
def registerServer(request: HttpResponse)  -> HttpResponse:
    t = 'serverRegistration.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        name = request.POST.get('name', '').strip()
        user = request.POST.get('user', '').strip()
        password = request.POST.get('password', '').strip()
        ip = request.POST.get('IP', '').strip()
        errores = []

        if not name or user or password or ip:
            server_registration_log.info("Se pasaron parametros vacios")
            errores.append(ERROR_MESSAGES['empty_fields'])
            return render(request, t, {'errores': errores})
        
        if copy_key_serverRemote(user, ip, password):
            server_registration_log.info(f'Server {name} registrado con IP:{ip}')
            return render(request, t)
        else:
            errores.append(ERROR_MESSAGES['ssh_field'])
            return render(request, t, {'errores': errores})
        
