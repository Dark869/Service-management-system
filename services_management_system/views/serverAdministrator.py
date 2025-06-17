from django.http import HttpResponse
from django.shortcuts import render, redirect
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import verify_fingerprint, verify_service
import logging

@login_request
def serverAdministrator(request: HttpResponse)  -> HttpResponse:
    t = 'serverAdministrator.html'

    if request.method == 'GET':
        servers = models.servers.objects.all()
        serversName = []
        IPs = []

        for server in servers:
            serversName.append(server.name)
            IPs.append(server.ip_address)

        server = models.servers.objects.get(name=serversName[0])
        services = models.services.objects.filter(server=server)
        services_list = []

        for service in services:
            services_list.append(service.name)

        return render(request, t, {'IPs': IPs, 'services': services_list})
    elif request.method == 'POST':
        nameService = request.POST.get('nameservice', '').strip()
        nameServer = request.POST.get('nameserver', '').strip()
        errores = []
        exito = []

        return render(request, t, {'IPs': IPs})