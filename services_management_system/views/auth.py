from django.http import HttpResponse
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

def login(request: HttpResponse) -> HttpResponse:
    if request.session.get('logged'):
        return redirect('/')

    t = 'login.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        passwd = request.POST.get('passwd', '').strip()
        captcha_token = request.POST.get('g-recaptcha-response', '').strip()
        errores = []

        if not captcha_token or not recaptcha_verify(captcha_token):
            errores.append(ERROR_MESSAGES['captcha_not_verified'])
            return render(request, t, {'errores': errores})

        if not email or not passwd:
            errores.append(ERROR_MESSAGES['empty_fields'])
            return render(request, t, {'errores': errores})

        user_auth_data = models.AuthData.objects.filter(email=email).values("password").first()

        if not user_auth_data:
            errores.append(ERROR_MESSAGES['invalid_credentials'])
            return render(request, t, {'errores': errores})

        if check_hash(passwd, user_auth_data['password']):
            user = models.User.objects.filter(auth_data__email=email).values("username").first()
            if not user:
                errores.append(ERROR_MESSAGES['invalid_credentials'])
                return render(request, t, {'errores': errores})
            request.session['logged'] = True
            request.session['user'] = email
            request.session['2fa_verified'] = False
            if not generate_code_2fa(request.session.get('user')):
                errores.append(ERROR_MESSAGES['error_generating_code'])
                return render(request, t, {'errores': errores})
            return redirect('/verify2fa')
        else:
            errores.append(ERROR_MESSAGES['invalid_credentials'])
            return render(request, t, {'errores': errores})

def logout(request: HttpResponse) -> HttpResponse:
    if request.method == 'GET':
        request.session.flush()
        return redirect('/')