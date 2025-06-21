from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from services_management_system.utils.hashing import check_hash
from db import models
from services_management_system.utils.recaptchaVerify import recaptcha_verify
from services_management_system.utils.generateCode2FA import generate_code_2fa

ERROR_MESSAGES = {
    'empty_fields': 'El usuario o contraseña no pueden estar vacíos',
    'invalid_credentials': 'El usuario o contraseña no son correctos',
    'captcha_not_verified': 'Captcha no verificado',
    'error_generating_code': 'Error al generar el código de verificación',
}

def login(request: HttpResponse) -> HttpResponse | JsonResponse:
    if request.session.get('logged'):
        return redirect('/')

    t = 'login.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        passwd = request.POST.get('passwd', '').strip()
        captcha_token = request.POST.get('g_recaptcha_response', '').strip()

        if not captcha_token or not recaptcha_verify(captcha_token):
            return JsonResponse({'status': "error" ,'message': ERROR_MESSAGES['captcha_not_verified']}, status=400)

        if not email or not passwd:
            return JsonResponse({'status': "error" ,'message': ERROR_MESSAGES['invalid_credentials']}, status=400)

        user_auth_data = models.AuthData.objects.filter(email=email).values("password").first()

        if not user_auth_data:
            return JsonResponse({'status': "error" ,'message': ERROR_MESSAGES['invalid_credentials']}, status=400)

        if check_hash(passwd, user_auth_data['password']):
            user = models.User.objects.filter(auth_data__email=email).values("username").first()
            if not user:
                return JsonResponse({'status': "error" ,'message': ERROR_MESSAGES['invalid_credentials']}, status=400)
            request.session['logged'] = True
            request.session['user'] = email
            request.session['2fa_verified'] = False
            if not generate_code_2fa(request.session.get('user')):
                return JsonResponse({'status': "error" ,'message': ERROR_MESSAGES['error_generating_code']}, status=500)
            return JsonResponse({'status': "success", 'message': 'Inicio de sesión exitoso.', 'redirectUrl': '/verify2fa/'}, status=200)
        else:
            return JsonResponse({'status': "error" ,'message': ERROR_MESSAGES['invalid_credentials']}, status=400)

def logout(request: HttpResponse) -> HttpResponse:
    if request.method == 'GET':
        request.session.flush()
        return redirect('/login')