from services_management_system.middlewares.loginRequest import login_request
from django.http import JsonResponse
from services_management_system.utils.generateCode2FA import generate_code_2fa

@login_request
def renew_otp(request):
    if request.method == 'GET':
        user = request.session.get('user')
        generate_code_2fa(user)
        return JsonResponse({"message": "Codigo renovado correctamente", "status": "success"}, status=200)