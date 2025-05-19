from django.shortcuts import render, redirect
from services_management_system.utils.hashing import check_password, hash_password
from db import models
from services_management_system.utils.recaptchaVerify import recaptchaVerify

ERROR_MESSAGES = {
    'empty_fields': 'El usuario o contraseña no pueden estar vacíos',
    'invalid_credentials': 'El usuario o contraseña no son correctos',
    'captcha_not_verified': 'Captcha no verificado'
}

def login(request):
    if request.session.get('logged'):
        return redirect('/')

    t = 'login.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        passwd = request.POST.get('passwd', '').strip()
        captchaToken = request.POST.get('g-recaptcha-response', '').strip()
        errores = []

        if not captchaToken or not recaptchaVerify(captchaToken):
            errores.append(ERROR_MESSAGES['captcha_not_verified'])
            return render(request, t, {'errores': errores})

        if not email or not passwd:
            errores.append(ERROR_MESSAGES['empty_fields'])
            return render(request, t, {'errores': errores})

        user_auth_data = models.AuthData.objects.filter(email=email).values("password").first()

        if not user_auth_data:
            errores.append(ERROR_MESSAGES['invalid_credentials'])
            return render(request, t, {'errores': errores})

        if check_password(passwd, user_auth_data['password']):
            user = models.User.objects.filter(auth_data__email=email).values("username").first()
            if not user:
                errores.append(ERROR_MESSAGES['invalid_credentials'])
                return render(request, t, {'errores': errores})
            request.session['logged'] = True
            request.session['user'] = user['username']
            return redirect('/')
        else:
            errores.append(ERROR_MESSAGES['invalid_credentials'])
            return render(request, t, {'errores': errores})
