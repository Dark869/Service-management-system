from django.http import JsonResponse, HttpResponse
from db import models
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.ssh import status_service

@login_request
def server_Administrator(request: HttpResponse) -> HttpResponse:
    if request.method == 'GET':
        name_server = request.GET.get('server_name', '').strip()

        if not name_server:
            return JsonResponse({'status': 'error', 'message': 'Parámetro "server_name" vacío'}, status=400)

        try:
            server_unic = models.servers.objects.get(name=name_server)
        except models.servers.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Servidor no encontrado'}, status=404)

        services = models.services.objects.filter(server=server_unic)
        services_status = {}

        for service in services:
            status = status_service(server_unic.ip_address, service.name)
            services_status[service.name] = status

        return JsonResponse({
            'status': 'success',
            'server': name_server,
            'services': services_status
        })

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
